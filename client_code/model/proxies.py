import itertools

from . import events
from .marks import Field, build_marks
from .utils import clean_record_key


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

    # This needs probably subclassing of the Filter object and a genertor function to
    # decide which one to instantiate based on the javascript filterType attribute.
    # The abstract Filter class does not offer a way to get the filter vlaue because
    # it is abstract
    @property
    def applied_values(self):
        if self.filter_type == "categorical":
            result = [v.nativeValue for v in self.appliedValues]
        elif self.filter_type == "range":
            result = (self.minValue.nativeValue, self.maxValue.nativeValue)
        elif self.filter_type == "relative-date":
            result = self.periodType
        elif self.filter_type == "hierarchical":
            # Borderline NotImplementedError in the JS library
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
    def name(self):
        return self._proxy.name

    @property
    def value(self):
        return self._proxy.currentValue


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

    pass


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

    # Feels like we need a similar method at the dashboard level that iterates through
    # all worksheets, returning first match
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
        return list(self._proxy.getParametersAsync())

    @property
    def data_sources(self):
        return list(self._proxy.getDataSourcesAsync())

    def register_event_handler(self, event_type, handler, session):
        events.register_event_handler(event_type, handler, self, session)


class Dashboard:
    """Wrapper for a tableau Dashboard

    https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html
    """

    def __init__(self):
        self._proxy = None
        self._worksheets = {}

    def __getitem__(self, idx):
        try:
            return self._worksheets[idx]
        except KeyError:
            raise KeyError(
                f"Worksheet {idx} doesn't exist. Worksheets in dashboard: {self._worksheets}"
            )

    def refresh(self):
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

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
        if self.proxy is None:
            return []
        return [Parameter(p) for p in self.proxy.getParametersAsync()]

    @property
    def name(self):
        if self.proxy is None:
            return None
        return self.proxy.name

    def refresh_data_sources(self):
        data_sources_generator = (ws.data_sources for ws in self.worksheets)
        data_sources = set(itertools.chain(*data_sources_generator))
        for ds in data_sources:
            ds.refreshAsync()

    def register_event_handler(self, event_type, handler, session):
        for ws in self.worksheets:
            ws.register_event_handler(event_type, handler, session)
