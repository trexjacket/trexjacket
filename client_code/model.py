import itertools

from .events import FILTER_CHANGED, PARAMETER_CHANGED, SELECTION_CHANGED


class TableauProxy:
    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, name):
        return getattr(self._proxy, name)


class Mark:
    """Wrapper for the data content of a selected tableau mark"""

    def __init__(self, **attrs):
        self.__dict__ = attrs

    def __str__(self):
        return str(self.__dict__)


class DataTable(TableauProxy):
    """Wrapper for a tableau DataTable

    https://tableau.github.io/extensions-api/docs/interfaces/datatable.html
    """

    @property
    def records(self):
        keys = [c.fieldName for c in self._proxy.columns]
        return [
            {
                attr[0]: attr[1]
                for attr in zip(keys, [data_value.nativeValue for data_value in row])
            }
            for row in self._proxy.data
        ]


class Field(TableauProxy):
    """Wrapper for a tableau Field

    https://tableau.github.io/extensions-api/docs/interfaces/field.html
    """

    @property
    def name(self):
        return self._proxy.name


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


class Worksheet(TableauProxy):
    """Wrapper for a tableau Worksheet

    https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html
    """

    @property
    def selected(self):
        datatable = DataTable(self._proxy.getSelectedMarksAsync()["data"][0])
        return datatable.records

    @property
    def filters(self):
        return [Filter(f) for f in self._proxy.getFiltersAsync()]

    @property
    def parameters(self):
        return list(self._proxy.getParametersAsync())

    @property
    def data_sources(self):
        return list(self._proxy.getDataSourcesAsync())


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

    def refresh_data_sources(self):
        data_sources_generator = (ws.data_sources for ws in self.worksheets)
        data_sources = set(itertools.chain(*data_sources_generator))
        for ds in data_sources:
            ds.refreshAsync()


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
        self._tableau_event_types = {
            FILTER_CHANGED: self._tableau.TableauEventType.FilterChanged,
            PARAMETER_CHANGED: self._tableau.TableauEventType.ParameterChanged,
            SELECTION_CHANGED: self._tableau.TableauEventType.MarkSelectionChanged,
        }
        self._proxies = {
            self._tableau.TableauEventType.FilterChanged: FilterChangedEvent,
            self._tableau.TableauEventType.MarkSelectionChanged: MarksSelectedEvent,
            self._tableau.TableauEventType.ParameterChanged: ParameterChangedEvent,
        }

    def tableau_event(self, event_type):
        try:
            return self._tableau_event_types[event_type]
        except KeyError:
            raise ValueError(f"Unknown event type: {event_type}")

    def proxy(self, event):
        return self._proxies[event._type](event)
