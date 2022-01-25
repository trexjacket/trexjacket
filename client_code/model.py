from anvil.js.window import tableau

tableau.extensions.initializeAsync()


class Mark:
    """Wrapper for the data content of a selected tableau mark"""

    def __init__(self, **attrs):
        self.__dict__ = attrs

    def __str__(self):
        return str(self.__dict__)


class DataTable:
    """Wrapper for a tableau DataTable

    https://tableau.github.io/extensions-api/docs/interfaces/datatable.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

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


class Field:
    """Wrapper for a tableau Field

    https://tableau.github.io/extensions-api/docs/interfaces/field.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

    @property
    def name(self):
        return self._proxy.name


class Filter:
    """Wrapper for a tableau Filter

    https://tableau.github.io/extensions-api/docs/interfaces/filter.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

    @property
    def field_name(self):
        return self._proxy.fieldName

    @property
    def filter_type(self):
        return self._proxy.filterType

    @property
    def field(self):
        return Field(self._proxy.getFieldAsync())


class Parameter:
    """Wrapper for a tableau Parameter

    https://tableau.github.io/extensions-api/docs/interfaces/parameter.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

    @property
    def name(self):
        return self._proxy.name

    @property
    def value(self):
        return self._proxy.currentValue


class Worksheet:
    """Wrapper for a tableau Worksheet

    https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

    @property
    def selected(self):
        datatable = DataTable(self._proxy.getSelectedMarksAsync()["data"][0])
        return [Mark(**record) for record in datatable.records]

    @property
    def filters(self):
        return [Filter(f) for f in self._proxy.getFiltersAsync()]

    @property
    def parameters(self):
        return list(self._proxy.getParametersAsync())


class Dashboard:
    """Wrapper for a tableau Dashboard

    https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html
    """

    def __init__(self):
        try:
            self._proxy = tableau.extensions.dashboardContent.dashboard
        except AttributeError:
            raise AttributeError("Cannot find a tableau dashboard in this page")
        self._worksheets = {}
        self.refresh()

    def __getitem__(self, idx):
        return self._worksheets(idx)

    def refresh(self):
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

    @property
    def worksheets(self):
        return self._worksheets.values()

    @property
    def parameters(self):
        return [Parameter(p) for p in self._proxy.getParametersAsync()]


class MarksSelectedEvent:
    """Wrapper for a tableau MarksSelectedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/marksselectedevent.html
    """

    def __init__(self, proxy):
        self._proxy = proxy

    @property
    def worksheet(self):
        return Worksheet(self._proxy._worksheet)


class FilterChangedEvent:
    """Wrapper for a tableau FilterChangedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/filterchangedevent.html
    """

    def __init__(self, proxy):
        self._proxy = proxy


class ParameterChangedEvent:
    """Wrapper for a tableau ParameterChangedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/parameterchangedevent.html
    """

    def __init__(self, proxy):
        self._proxy = proxy


event_types = {
    "filter_changed": tableau.TableauEventType.FilterChanged,
    "selection_changed": tableau.TableauEventType.MarkSelectionChanged,
    "parameter_changed": tableau.TableauEventType.ParameterChanged,
}

proxies = {
    tableau.TableauEventType.FilterChanged: FilterChangedEvent,
    tableau.TableauEventType.MarkSelectionChanged: MarksSelectedEvent,
    tableau.TableauEventType.ParameterChanged: ParameterChangedEvent,
}


