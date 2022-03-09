import itertools
from time import sleep

import anvil

from .._anvil_extras.injection import HTMLInjector
from .._anvil_extras.messaging import Publisher
from .._anvil_extras.non_blocking import call_async
from .._logging import Logger
from . import events
from .marks import Field, build_marks
from .utils import clean_record_key

CDN_URL = "https://cdn.jsdelivr.net/gh/tableau/extensions-api/lib/tableau.extensions.1.latest.js"  # noqa


def _inject_tableau():
    injector = HTMLInjector()
    injector.cdn(CDN_URL)

    from anvil.js.window import tableau

    return tableau


class Tableau:
    current_session = None

    @classmethod
    def session(cls):
        if not cls.current_session:
            cls.current_session = Tableau()
        return cls.current_session

    def __init__(self, timeout=2):
        if self.current_session:
            raise ValueError("You've already started a session. Use Tableau.session().")

        self.logger = Logger()
        self.logger.log("Starting new session")
        self._initializing = True
        self.timeout = timeout
        self.publisher = Publisher()
        self.event_type_mapper = EventTypeMapper()
        self.dashboard = Dashboard(self)
        self._tableau = _inject_tableau()
        async_call = call_async(self._tableau.extensions.initializeAsync)
        async_call.on_result(self._on_init)
        async_call.on_error(self.handle_error)
        self.available

    def _on_init(self, result):
        self.dashboard.proxy = self._tableau.extensions.dashboardContent.dashboard
        self.event_type_mapper.tableau = self._tableau
        self._initializing = False

    def handle_error(self, err):
        self.logger.log(err)
        anvil.Notification("Failed to initialize tableau", style="danger").show()

    @property
    def available(self):
        waited = 0
        step = 0.1
        if self._initializing:
            self.logger.log(
                "Dashboard is still initialising. "
                f"Waiting for a max of {self.timeout} seconds..."
            )
        while self._initializing and waited <= self.timeout:
            sleep(step)
            waited += step
        return self.dashboard.proxy is not None

    @property
    def extensions_api(self):
        """This provides access to the raw Tableau Extensions API.
        This can be used to access parts of the API that is not handled by the
        Anvil Tableau Extension framework yet.

        For example, if you want to access underlying data for the first sheet,
        you can call:
        dashboard = tableau.extensions_api.extensions.dashboardContent.dashboard
        dashboard.worksheets[0].getUnderlyingDataAsync()

        Note that this maps the Tableau Extensions API, and returns JavaScript
        Proxy Objects.

        For more information, see:
        https://anvil.works/docs/client/javascript/accessing-javascript
        """
        return self._tableau


class TableauProxy:
    """A base class for those requiring a Tableau proxy object"""

    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, name):
        return getattr(self._proxy, name)


class DataTable(TableauProxy):
    """Wrapper for a tableau DataTable

    https://tableau.github.io/extensions-api/docs/interfaces/datatable.html
    """

    @property
    def records(self):
        keys = [c.fieldName for c in self._proxy.columns]
        return [
            {
                clean_record_key(attr[0]): (
                    attr[1] if attr[0] != "Measure Names" else attr[2]
                )
                for attr in zip(
                    keys,
                    [data_value.nativeValue for data_value in row],
                    [data_value.formattedValue for data_value in row],
                )
            }
            for row in self._proxy.data
        ]


class Filter:
    """Wrapper for a tableau Filter

    https://tableau.github.io/extensions-api/docs/interfaces/filter.html
    """

    def __init__(self, proxy):
        self._proxy = proxy
        self.worksheet = None

    def __getattr__(self, name):
        return getattr(self._proxy, name)

    @property
    def field_name(self):
        return self._proxy.fieldName

    def set_filter_value(self, new_values, method="replace"):
        self.worksheet.apply_filter(self.field_name, new_values, method)

    @property
    def applied_values(self):
        if self.filter_type == "categorical":
            result = [v.nativeValue for v in self.appliedValues]
        elif self.filter_type == "range":
            result = (self.minValue.nativeValue, self.maxValue.nativeValue)
        elif self.filter_type == "relative-date":
            result = self.periodType
        elif self.filter_type == "hierarchical":
            result = "Hierarchical filter"

        return result

    @applied_values.setter
    def applied_values(self, new_values):
        self.set_filter_value(new_values)

    @property
    def domain(self):
        return [v.nativeValue for v in self._proxy.getDomainAsync("database").values]

    @property
    def relevant_domain(self):
        return [v.nativeValue for v in self._proxy.getDomainAsync("relevant").values]

    @property
    def filter_type(self):
        return self._proxy.filterType

    @property
    def field(self):
        return Field(self._proxy.getFieldAsync())


class Parameter(TableauProxy):
    """Wrapper for a tableau Parameter

    https://tableau.github.io/extensions-api/docs/interfaces/parameter.html
    """

    @property
    def domain(self):
        return self.allowable_values()

    @property
    def data_type(self):
        return self._proxy.dataType

    def allowable_values(self):
        return self._proxy.allowableValues

    def change_value(self, new_value):
        self._proxy.changeValueAsync(new_value)

    @property
    def name(self):
        return self._proxy.name

    @property
    def value(self):
        return self._proxy.currentValue.nativeValue

    @value.setter
    def value(self, new_value):
        self.change_value(new_value)

    def register_event_handler(self, handler):
        self._listener = events.register_event_handler(
            events.PARAMETER_CHANGED, handler, self, Tableau.session()
        )

    def remove_event_handler(self):
        if hasattr(self, "_listener") and self._listener:
            self._proxy.removeEventListener(events.PARAMETER_CHANGED, self._listener)
            self._listener = None

    def __repr__(self):
        return f"Parameter: '{self.name}', with current value: {self.value}"


class MarksSelectedEvent(TableauProxy):
    """Wrapper for a tableau MarksSelectedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/marksselectedevent.html
    """

    @property
    def worksheet(self):
        return Worksheet(self._proxy._worksheet)


class FilterChangedEvent(TableauProxy):
    """Wrapper for a tableau FilterChangedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/filterchangedevent.html
    """

    @property
    def filter(self):
        f = Filter(self._proxy.getFilterAsync())
        f.worksheet = self.worksheet
        return f

    @property
    def worksheet(self):
        return Worksheet(self._proxy._worksheet)


class ParameterChangedEvent(TableauProxy):
    """Wrapper for a tableau ParameterChangedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/parameterchangedevent.html
    """

    @property
    def parameter(self):
        return Parameter(self._proxy.getParameterAsync())


class EventTypeMapper:
    def __init__(self):
        self._tableau = None
        self._tableau_event_types = None
        self._proxies = None

    @property
    def tableau(self):
        return self._tableau

    @tableau.setter
    def tableau(self, value):
        self._tableau = value
        event_type = self._tableau.TableauEventType
        self._tableau_event_types = {
            events.FILTER_CHANGED: event_type.FilterChanged,
            events.PARAMETER_CHANGED: event_type.ParameterChanged,
            events.SELECTION_CHANGED: event_type.MarkSelectionChanged,
        }
        self._proxies = {
            event_type.FilterChanged: FilterChangedEvent,
            event_type.MarkSelectionChanged: MarksSelectedEvent,
            event_type.ParameterChanged: ParameterChangedEvent,
        }

    def tableau_event(self, event_type):
        try:
            return self._tableau_event_types[event_type]
        except KeyError:
            raise ValueError(f"Unknown event type: {event_type}")

    def proxy(self, event):
        return self._proxies[event._type](event)


class Worksheet(TableauProxy):
    """Wrapper for a tableau Worksheet

    https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html
    """

    @property
    def selected_records(self):
        data = self._proxy.getSelectedMarksAsync()["data"]
        datatables = (DataTable(table) for table in data)
        return list(itertools.chain(*[dt.records for dt in datatables]))

    @property
    def selected_marks(self):
        data = self._proxy.getSelectedMarksAsync()["data"]
        datatables = (DataTable(table) for table in data)
        records = list(itertools.chain(*[dt.records for dt in datatables]))
        return build_marks(records)

    @property
    def filters(self):
        all_filters = [Filter(f) for f in self._proxy.getFiltersAsync()]
        for f in all_filters:
            f.worksheet = self

        return all_filters

    def get_filter(self, filter_name):
        specified_filter = [f for f in self.filters if f.field_name == filter_name]
        if not specified_filter:
            raise KeyError(
                f"No filter matching field_name {filter_name}. "
                f"Worksheet filters: {[f.field_name for f in self.filters]}"
            )

        specified_filter = specified_filter[0]
        specified_filter.worksheet = self
        return specified_filter

    def apply_filter(self, field_name, values, update_type="replace"):
        if not isinstance(values, list):
            values = [values]

        print(
            f"applying filter async: {field_name} "
            f"filtered to {values} with method {update_type}"
        )
        self._proxy.applyFilterAsync(field_name, values, update_type)
        print("filter applied")

    @property
    def parameters(self):
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        p = [Parameter(p) for p in self.parameters if p.name == parameter_name]
        if not p:
            raise KeyError(
                f"No matching parameter found for {parameter_name}. "
                f"Parameters on Sheet: {[p.name for p in self.parameters]}"
            )
        else:
            return p[0]

    @property
    def data_sources(self):
        return list(self._proxy.getDataSourcesAsync())

    def register_event_handler(self, event_type, handler):
        if event_type in [
            "selection_changed",
            "filter_changed",
            events.SELECTION_CHANGED,
            events.FILTER_CHANGED,
        ]:
            events.register_event_handler(event_type, handler, self, Tableau.session())

        elif event_type in ["parameter_changed", events.PARAMETER_CHANGED]:
            for p in self.parameters:
                p.register_event_handler(handler)

        else:
            raise NotImplementedError(
                "You can only set selection_changed, filter_changed, or "
                f"parameter_changed from the Sheet object. You tried: {event_type}"
            )


class Dashboard:
    """Wrapper for a tableau Dashboard

    https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html
    """

    def __init__(self, session):
        self._proxy = None
        self._worksheets = {}
        self.session = session

    def __getitem__(self, idx):
        try:
            return self._worksheets[idx]
        except KeyError:
            raise KeyError(
                f"Worksheet {idx} doesn't exist. "
                f"Worksheets in dashboard: {self._worksheets}"
            )

    def refresh(self):
        self._worksheets = {
            ws.name: Worksheet(ws, self.session) for ws in self._proxy.worksheets
        }

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, value):
        self._proxy = value
        if value is not None:
            self.refresh()

    @property
    def worksheets(self):
        return list(self._worksheets.values())

    @property
    def parameters(self):
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        p = [Parameter(p) for p in self.parameters if p.name == parameter_name]
        if not p:
            raise KeyError(
                f"No matching parameter found for {parameter_name}. "
                f"Parameters on Sheet: {[p.name for p in self.parameters]}"
            )
        else:
            return p[0]

    @property
    def name(self):
        if self.proxy is None:
            return None
        return self.proxy.name

    @property
    def datasources(self):
        return self._proxy.getAllDataSourcesAsync()

    def refresh_data_sources(self):
        data_sources_generator = (ws.data_sources for ws in self.worksheets)
        data_sources = set(itertools.chain(*data_sources_generator))
        for ds in data_sources:
            ds.refreshAsync()

    def register_event_handler(self, event_type, handler):
        if event_type in [
            "selection_changed",
            "filter_changed",
            events.SELECTION_CHANGED,
            events.FILTER_CHANGED,
        ]:
            for ws in self.worksheets:
                ws.register_event_handler(event_type, handler)

        elif event_type in ["parameter_changed", events.PARAMETER_CHANGED]:
            for p in self.parameters:
                p.register_event_handler(handler)

        else:
            raise NotImplementedError(
                "You can only set selection_changed, filter_changed, or"
                f"parameter_changed from the Dashboard object. You passed: {event_type}"
            )
