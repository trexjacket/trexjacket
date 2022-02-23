import itertools
import re

from .events import FILTER_CHANGED, PARAMETER_CHANGED, SELECTION_CHANGED


class Dimension:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Dimension(name={self.name!r}, value={self.value!r})"


class Mark:
    def __init__(self, name, value, dimensions=None, aggregation=None):
        self.name = name
        self.value = value
        self.dimensions = {} if dimensions is None else dimensions
        self.aggregation = aggregation

    def __getattr__(self, name):
        if name in self.dimensions:
            return self.dimensions[name].value
        else:
            raise AttributeError(f"{name} not found")

    def __repr__(self):
        return (
            f"Mark(name={self.name!r}, value={self.value!r}, "
            f"dimensions={self.dimensions}, aggregation={self.aggregation!r})"
        )


class MarksCollection:
    def __init__(self, marks):
        self.marks = marks

    def __getitem__(self, key):
        return self.marks[key]

    def __getattr__(self, name):
        return self.marks[name]

    def __len__(self):
        return len(self.marks)

    def __iter__(self):
        return iter(self.marks.values())

    def __repr__(self):
        return f"MarksCollection({self.marks})"


aggregation_pattern = re.compile(r"(^.*?)\((.*)\)$")


def _marks(record):
    result = {}
    dimensions = {}
    for key, value in record.items():
        match = aggregation_pattern.search(key)
        if match:
            name = match.group(2)
            aggregation = match.group(1)
            result[name] = Mark(name, value, aggregation=aggregation)
        else:
            dimensions[key] = Dimension(key, value)

    for mark in result.values():
        mark.dimensions = dimensions
    return result


def marks_collection(records):
    marks = {key: mark for record in records for key, mark in _marks(record).items()}
    return MarksCollection(marks)


class TableauProxy:
    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, name):
        return getattr(self._proxy, name)


def _clean_record_key(key):
    return key.replace("(generated)", "").strip().lower().replace(" ", "_")


class DataTable(TableauProxy):
    """Wrapper for a tableau DataTable

    https://tableau.github.io/extensions-api/docs/interfaces/datatable.html
    """

    @property
    def records(self):
        keys = [c.fieldName for c in self._proxy.columns]
        return [
            {
                _clean_record_key(attr[0]): attr[1]
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
        return marks_collection(datatable.records)

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

