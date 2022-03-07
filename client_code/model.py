import itertools
import re

from .events import FILTER_CHANGED, PARAMETER_CHANGED, SELECTION_CHANGED


class Dimension:
    """Represents a dimension of a selected Mark"""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Dimension(name={self.name!r}, value={self.value!r})"

    def __hash__(self):
        return hash((self.name, self.value))

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value


class Mark:
    """Basically a class for Dan to throw some spaghetti to see what sticks

    Usage:
    mark.dimensions: a tuple of the identifying dimensions
    mark.identifier: a tuple identifying the mark
    mark.measures: a tuple of the underlying data
    mark.values:  a tuple of the actual data that is associated with this mark,
    mapped to measures

    Marks are accessible by case-insensitive dictionary lookup
    i.e. a mark can be accessed mark['profit'] and this will return the value
    associated with any of:
      mark measure SUM(Profit)
      mark measure (Profit)
    """

    def __init__(self, dimensions):
        self.values_dict = dict()
        self.dimensions = dimensions

    @property
    def identifier(self):
        return tuple([d.value for d in self.dimensions])

    @property
    def identifying_properties(self):
        return (d.name for d in self.dimensions)

    @property
    def value(self):
        return self.values_dict.values[0]

    @property
    def values(self):
        return self.values_dict.values

    @property
    def measures(self):
        return list(self.values_dict.keys())

    def __getitem__(self, key):
        return self.values_dict[_clean_record_key(key)]

    def get(self, key):
        return self.values_dict.get(_clean_record_key(key))

    def __repr__(self):
        return f"DansMark: Identified by {self.dimensions}, values: {self.values_dict}"


def _marks(records):
    """Generates Dans Marks"""
    # we iterate through all records.
    # Some "Marks" can be assembled from multiple records if they share a common
    # identifier (frozen set of dimensions)
    # This is not really known until we have iterated through all records
    # We do rely on a record having a complete set of dimensions, or they will be
    # assembled separately (i.e. dimensions
    # must fully overlap for us to group them)
    dans_marks = dict()
    for record in records:
        all_dimensions = set()
        all_values = dict()
        measure_flag = False
        for key, value in record.items():
            this_value = None
            this_dimension = None
            aggregation_match = aggregation_pattern.search(key)
            datetime_match = datetime_pattern.search(key)
            category_match = isinstance(value, str)
            is_measure_name = key == "measure_names"
            is_measure_value = key == "measure_values"

            if is_measure_name:
                measure_flag = True
                measure_name = value

            elif is_measure_value:
                measure_flag = True
                measure_value = value

            elif datetime_match:
                name = datetime_match.group(2)
                this_dimension = Dimension(name, value)

            elif category_match:
                this_dimension = Dimension(key, value)

            elif aggregation_match:
                name = aggregation_match.group(2)
                # for now we don't use this since my model is too basic
                # aggregation = aggregation_match.group(1)
                this_value = {_clean_record_key(name): value}

            else:
                this_value = {_clean_record_key(key): value}

            if this_dimension:
                all_dimensions.add(this_dimension)
            elif this_value:
                all_values.update(this_value)

        if measure_flag:
            all_values[_clean_record_key(measure_name)] = measure_value

        all_dimensions = frozenset(all_dimensions)

        if all_dimensions in dans_marks:
            dans_marks[all_dimensions].values_dict.update(all_values)

        else:
            new_mark = Mark(all_dimensions)
            new_mark.values_dict = all_values
            dans_marks[all_dimensions] = new_mark

    return list(dans_marks.values())


aggregation_pattern = re.compile(r"(^agg|sum)\((.*)\)$")
datetime_pattern = re.compile(r"(^month)\((.*)\)$")


class TableauProxy:
    """A base class for those requiring a Tableau proxy object"""

    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, name):
        return getattr(self._proxy, name)


def _clean_record_key(key):
    """Clean the record keys from tableau"""
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
                _clean_record_key(attr[0]): (
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
    def selected_records(self):
        data = self._proxy.getSelectedMarksAsync()["data"]
        datatables = (DataTable(table) for table in data)
        return list(itertools.chain(*[dt.records for dt in datatables]))

    @property
    def selected_marks(self):
        data = self._proxy.getSelectedMarksAsync()["data"]
        datatables = (DataTable(table) for table in data)
        records = list(itertools.chain(*[dt.records for dt in datatables]))
        return _marks(records)

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
