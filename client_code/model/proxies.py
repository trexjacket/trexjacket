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


class Filter(TableauProxy):
    """Wrapper for a tableau Filter

    https://tableau.github.io/extensions-api/docs/interfaces/filter.html
    """

    @property
    def field_name(self):
        return self._proxy.fieldName

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

    pass


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
        return [Filter(f) for f in self._proxy.getFiltersAsync()]

    @property
    def parameters(self):
        return list(self._proxy.getParametersAsync())

    @property
    def data_sources(self):
        return list(self._proxy.getDataSourcesAsync())

    def register_event_handler(self, event_type, handler, session):
        events.register_event_handler(event_type, handler, [self], session.mapper)


class Dashboard:
    """Wrapper for a tableau Dashboard

    https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html
    """

    def __init__(self):
        self._proxy = None
        self._worksheets = {}

    def __getitem__(self, idx):
        return self._worksheets(idx)

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
        return self._worksheets.values()

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
