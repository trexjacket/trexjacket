import datetime as dt
import itertools

import anvil
from anvil import tableau
from anvil.code_completion_hints import EventHandler, function_type_hint
from anvil.js import report_exceptions

from .. import exceptions
from .._utils import _dejsonify, _jsonify
from . import events
from ._utils import (
    _clean_columns,
    _to_js_date,
    clean_record_key,
    cleanup_measures,
    native_value_date_handler,
)

_event_cache = {}

import json


def _suppress_duplicate_events(event_handler):
    """Wrap an event handler function to cope with duplicate events.

    Filter change events are often duplicated. This function is used within the
    registration of an event handler to replace the function from the user with one
    that will only fire once for any given event.

    Parameters
    ----------
    event_handler : function
        The event handling function provided by the user

    Returns
    ----------
    function
    """

    def suppressing_handler(event):
        """An event handler that caches events and calls the original handler only if
        the event does not exist in the cache
        """
        now = dt.datetime.now()
        del_keys = []
        for k, v in _event_cache.items():
            if now - v > dt.timedelta(seconds=0.5):
                del_keys.append(k)

        for k in del_keys:
            del _event_cache[k]

        if event not in _event_cache:
            _event_cache[event] = now
            event_handler(event)

    return suppressing_handler


class NoDefault:
    pass


class TableauProxy:
    """A base class for those requiring a Tableau proxy object.

    Allows for access of the underlying Tableau JS object using the ``_proxy`` attribute.
    """

    def __init__(self, proxy):
        self._proxy = proxy
        try:
            self.id = getattr(proxy, self.identifier)
        except AttributeError:
            self.id = None

    def __getattr__(self, name):
        return getattr(self._proxy, name)

    def __eq__(self, other):
        self.id == other.id


class MarksSelectedEvent(TableauProxy):
    """Triggered when a user selects a mark on the Tableau dashboard.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/marksselectedevent.html>` and accessed through the ``MarksSelectedEvent`` object's ``._proxy`` attribute.
    """

    @property
    def worksheet(self):
        """The Tableau worksheet associated with generating the Selection Event.

        :type: :obj:`Worksheet`
        """
        return Worksheet(self._proxy._worksheet)

    def get_selected_marks(self, collapse_measures=False):
        """The data for the marks which were selected.
        If a deselection occured, an empty list is returned.

        Parameters
        ----------
        collapse_measures : bool
            Whether or not to try and collapse records on worksheets that use
            measure names / measure values. This often happens when getting summary
            data for dual axis visualizations.

        Returns
        --------
        records : list
            Data for the currently selected marks
        """
        return self.worksheet.get_selected_marks(collapse_measures)


class FilterChangedEvent(TableauProxy):
    """Triggered when a user changes a filter on a dashboard.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/filterchangedevent.html>` and accessed through the ``FilterChangedEvent`` object's ``._proxy`` attribute.
    """

    def __hash__(self):
        return hash(self.fieldName)

    def __eq__(self, other):
        return self.fieldName == other.fieldName

    @property
    def filter(self):
        """The filter that was changed.

        :type: :obj:`Filter`
        """
        f = self._proxy.getFilterAsync()
        return Filter._create_filter(f)

    @property
    def worksheet(self):
        """The worksheet that the filter is on.

        :type: :obj:`Worksheet`
        """
        return Worksheet(self._proxy._worksheet)


class ParameterChangedEvent(TableauProxy):
    """Triggered when a user changes a parameter on a dashboard.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/parameterchangedevent.html>` and accessed through the ``ParameterChangedEvent`` object's ``._proxy`` attribute.
    """

    @property
    def parameter(self):
        """The parameter that was changed.

        :type: :obj:`Parameter`
        """
        return Parameter(self._proxy.getParameterAsync())


class Field(TableauProxy):
    """Represents a field in Tableau.

    .. note::
        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/field.html>` and accessed through the ``_DataTable`` object's ``._proxy`` attribute.
    """

    @property
    def datasource(self):
        return Datasource(self._proxy.dataSource)


class Filter(TableauProxy):
    """A base class to represent a filter in Tableau."""

    @classmethod
    def _create_filter(cls, js_filter):
        """
        Returns an instance of one of the subclasses based on the proxy object's type.
        """
        if js_filter.filterType == "categorical":
            return CategoricalFilter(js_filter)
        elif js_filter.filterType == "hierarchical":
            return HierarchicalFilter(js_filter)
        elif js_filter.filterType == "range":
            return RangeFilter(js_filter)
        elif js_filter.filterType == "relative-date":
            return RelativeDateFilter(js_filter)
        else:
            raise TypeError(
                f"Filters of type {js_filter.filterType} are not supported."
            )

    @property
    def field_id(self):
        return self._proxy.fieldId

    @property
    def field_name(self):
        """The name of the field that has the filter applied."""
        return self._proxy.fieldName

    @property
    def filter_type(self):
        """The type of filter."""
        return self._proxy.filterType

    @property
    def worksheet_name(self):
        """The name of the parent worksheet that the filter is on."""
        return self._proxy.worksheetName

    @property
    def parent_worksheet(self):
        """The parent worksheet.

        :obj:`Worksheet`
        """
        return _Tableau.session().dashboard.get_worksheet(self.worksheet_name)

    @property
    def field(self):
        """The field that has the filter applied."""
        return Field(self._proxy.getFieldAsync())

    def clear(self):
        """This is helper method that clears a filter from it's parent worksheet."""
        if self.field_name.startswith("Action"):
            print("Warning! Calling clear on an action filter does nothing.")
            return
        #  Filters do not natively know about that dashboard or worksheet they are in,
        # so clearing them requires us to access the parent_worksheet
        self.parent_worksheet.clear_filter(self.field_name)

    def __str__(self):
        return f"Filter ({self.filter_type}) on the '{self.field_name}' field of the {self.parent_worksheet.name} worksheet."


class CategoricalFilter(Filter):
    """Represents a categorical filter in Tableau."""

    @property
    def applied_values(self):
        """The currently applied values to the filter."""
        if self.parent_worksheet:
            self._proxy = self.parent_worksheet.get_filter(self.field_name)._proxy

        if self.is_all_selected:
            return self.get_domain("database")["values"]

        return [native_value_date_handler(v.nativeValue) for v in self.appliedValues]

    @applied_values.setter
    def applied_values(self, values):
        self.parent_worksheet.apply_categorical_filter(self.field_name, values)

    @property
    def is_all_selected(self):
        """Whether or not the 'All' box is checked on the filter."""
        return self._proxy.isAllSelected

    @property
    def is_exclude_mode(self):
        """Whether or not the filter is in exclude mode."""
        return self._proxy.isExcludeMode

    def get_domain(self, domain_type="relevant"):
        """Returns the filter's domain.

        domain_type can either be 'database' or relevant'
        """
        raw_domain = self._proxy.getDomainAsync(domain_type)
        values = [
            native_value_date_handler(datavalue.nativeValue)
            for datavalue in raw_domain["values"]
        ]
        return {"type": raw_domain["type"], "values": values}

    def describe(self):
        """Returns a descriptive string about the filter."""

        def _first_5(array):
            s = ", ".join([str(x) for x in array[:5]])
            if len(array) > 5:
                s += f" ... ({len(array)} total)"
            return s

        return f"""
      Categorical Filter with applied values of {_first_5(self.applied_values)} and domain of {_first_5(self.get_domain('database')['values'])}
      """


class HierarchicalFilter(Filter):
    """Represents a Hierarchical Filter in Tableau. Currently no methods are wrapped, but attributes can be accessed using
    their camel case names listed in the Tableau Documentation.
    """

    def describe(self):
        """Returns a descriptive string about the filter."""
        return "Hierarchical Filter"


class RangeFilter(Filter):
    """Represents a Range Filter in Tableau."""

    @property
    def include_null_values(self):
        """Whether or not the range filter includes null values."""
        return self._proxy.includeNullValues

    @property
    def max(self):
        """The currently applied maximum value for the range filter. Date and datetime
        filters will return a UTC datetime.date or datetime.datetime object.
        """
        if self.parent_worksheet:
            self._proxy = self.parent_worksheet.get_filter(self.field_name)._proxy
        return native_value_date_handler(self.maxValue.nativeValue)

    @max.setter
    def max(self, value):
        if isinstance(value, (dt.date, dt.datetime)):
            min_value, max_value = _to_js_date(self.min), _to_js_date(value)
        else:
            min_value, max_value = self.min, value
        self.parent_worksheet.apply_range_filter(self.field_name, min_value, max_value)

    @property
    def min(self):
        """The currently applied minimum value for the range filter. Date and datetime
        filters will return a UTC datetime.date or datetime.datetime object.
        """
        if self.parent_worksheet:
            self._proxy = self.parent_worksheet.get_filter(self.field_name)._proxy
        return native_value_date_handler(self.minValue.nativeValue)

    @min.setter
    def min(self, value):
        if isinstance(value, (dt.date, dt.datetime)):
            min_value, max_value = _to_js_date(value), _to_js_date(self.max)
        else:
            min_value, max_value = value, self.max
        self.parent_worksheet.apply_range_filter(self.field_name, min_value, max_value)

    def get_domain(self, domain_type="relevant"):
        """Returns the filter's domain.

        domain_type can either be 'database' or relevant'
        """
        raw_domain = self._proxy.getDomainAsync(domain_type)
        return {
            "min": native_value_date_handler(raw_domain["min"].nativeValue),
            "max": native_value_date_handler(raw_domain["max"].nativeValue),
            "type": raw_domain["type"],
        }

    def describe(self):
        """Returns a descriptive string about the filter."""
        return f"""
      Range Filter on field '{self.field_name}', domain of {self.get_domain('database')['min']} to {self.get_domain('database')['max']}
      Min of {self.min} and max of {self.max} applied.
      Include nulls? ({self.include_null_values})
      """


class RelativeDateFilter(Filter):
    def describe(self):
        """Returns a descriptive string about the filter."""
        return f"""
      Relative Date Filter with an anchor date of {self._proxy.anchorDate}
      with {self._proxy.rangeN} {self._proxy.periodType} periods of {self._proxy.rangeType}
      """


class Parameter(TableauProxy):
    identifier = "id"

    """Represents a parameter in Tableau. Parameter values can be modified and read using this class.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/parameter.html>` and accessed through the ``Parameter`` object's ``._proxy`` attribute.
    """

    def __str__(self):
        return f"Parameter named '{self.name}'"

    @property
    def name(self):
        """The display name for this parameter.

        :type: str
        """
        return self._proxy.name

    @property
    def value(self):
        """The current value of the parameter."""
        self._refresh()
        return native_value_date_handler(self._proxy.currentValue.nativeValue)

    @value.setter
    def value(self, new_value):
        """Changes the DataValue representing the current value of the parameter.

        Parameters
        ----------
        new_value : DataValue
            DataValue representing the new value of the parameter.
        """
        self.change_value(new_value)

    @property
    def data_type(self):
        """The type of data this parameter holds. One of (bool | date | date-time | float | int | spatial | string).

        :type: str
        """
        return self._proxy.dataType

    @property
    def allowable_values(self):
        """Returns the allowable set of values this parameter can take.

        Returns
        --------
        The allowable set of values this parameter can take.
        """
        param_type = self._proxy.allowableValues.type  # All, List, or Range

        def _retrieve_value(val):
            """Retrieve the allowableValue field based on its data type.

            Parameters
            ------
            val : DataValue

            Returns
            ------
            Value parsed with either .formattedValue(), .nativeValue(), .value() depending on the
            data type of the parameter.
            """
            if self.data_type in ["date", "date-time"]:
                return native_value_date_handler(val.nativeValue)
            elif self.data_type == "float":
                try:
                    return float(val.nativeValue)
                except ValueError:
                    print(
                        "Warning, float conversion failed. Returning the formatted value of the parameter."
                    )
                    return val.formattedValue
            else:
                return val.nativeValue

        def _allvalues():
            raise ValueError(
                f'allowable_values is only available for "list", or "range" type filters, not "{param_type}"'
            )

        def _listvalues():
            return [
                _retrieve_value(d) for d in self._proxy.allowableValues.allowableValues
            ]

        def _rangevalues():
            mmin = self._proxy.allowableValues.minValue
            mmax = self._proxy.allowableValues.maxValue

            return {"min": _retrieve_value(mmin), "max": _retrieve_value(mmax)}

        valmapper = {"all": _allvalues, "list": _listvalues, "range": _rangevalues}

        return valmapper[param_type]()

    def change_value(self, new_value):
        """Modifies this parameter and assigns it a new value.

        The new value must fall within the domain restrictions defined by
        allowableValues.

        Parameters
        ----------
        new_value : string | number | boolean | Date
            The new value to assign to this parameter. Note: For changing Date
            parameters, UTC Date objects are expected.
        """
        self._proxy.changeValueAsync(new_value)

    def register_event_handler(self, handler):
        """Register an event handler that will be called whenever the parameter is changed.

        Note that the handler must take a ParameterChangedEvent instance as an argument.

        Parameters
        ----------
        handler : function
            Function that is called whenever the parameter is changed.
        """
        session = _Tableau.session()
        self._listener = session.register_event_handler(
            events.PARAMETER_CHANGED, handler, self
        )

    def unregister_event_handler(self, handler):
        session = _Tableau.session()
        session.unregister_event_handler(self, handler, events.PARAMETER_CHANGED)

    def unregister_all_event_handlers(self):
        session = _Tableau.session()
        session.unregister_all_event_handlers(self)

    def _refresh(self, parameter_changed_event=None):
        """Refreshes the object to reflect any changes in the dashboard."""
        self._proxy = _Tableau.session().dashboard.get_parameter(self.name)._proxy


class DataTable(TableauProxy):
    """Represents a datatable in Tableau.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/datatable.html>` and accessed through the ``_DataTable`` object's ``._proxy`` attribute.
    """

    @property
    def columns(self) -> dict:
        """Returns details on the columns in the datatable. {colname: coltype}

        :type: dict

        Example
        -------
        >>> ds = self.dashboard.get_worksheet('Sales Summary').datasources[0]
        >>> underlying_table = ds.get_underlying_table('Orders_6D2EF74F348B46BDA976A7AEEA6FB5C9')
        >>> underylying_table.columns
        {'Category': 'string', 'City': 'string', 'Country/Region': 'string', 'Customer ID': 'string'}
        """
        return _clean_columns(self._proxy.columns)

    def get_records(self, collapse_measures=False):
        """The records in the data table.

        :obj:`list` of :obj:`dict`
        """
        keys = [c.fieldName for c in self._proxy.columns]
        raw_records = [
            {
                clean_record_key(attr[0]): (
                    attr[1] if attr[0] != "Measure Names" else attr[2]
                )
                for attr in zip(
                    keys,
                    [
                        native_value_date_handler(data_value.nativeValue)
                        for data_value in row
                    ],
                    [data_value.formattedValue for data_value in row],
                )
            }
            for row in self._proxy.data
        ]
        if not raw_records:
            return raw_records
        if collapse_measures:
            return cleanup_measures(raw_records)

        if "Measure Names" in raw_records[0].keys():
            print(
                "Note: 'Measure Names' was found in the keys for these records.\n"
                "Set the collapse_measures argument to True in order to collapse these values.\n"
                "Your selection will not be affected by setting the collapse_measures argument to True."
            )
        return raw_records


class Datasource(TableauProxy):
    """Represents a Tableau data source.

    Note that Datasources in Tableau are often comprised of multiple logical tables. If your
    Datasource contains multiple logical tables you'll need to specify the id when using some methods.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/datasource.html>` and accessed through the ``Datasource`` object's ``._proxy`` attribute.
    """

    def __str__(self):
        return f"Datasource named '{self.name}'. Use the .underlying_table_info property to retrieve information about the underlying tables that make up the datasource."

    @property
    def columns(self):
        """The columns in the datasource, if the datasource contains a single logical table. If the datasource
        contains more than one logical table, a MultipleTablesException error is raised.
        """
        try:
            return self.get_underlying_table().columns
        except exceptions.MultipleTablesException:
            raise exceptions.MultipleTablesException(
                "More than one logical table exists in the datasource so you need\n"
                'to use the "get_underyling_table" method with a table id rather\n'
                "than accessing the columns directly:\n"
                ">>> datasource.get_underlying_table(table_id).columns\n"
                'A list of (caption, table_id) can be found using the "underlying_table_info" property\n'
                "(result of self.underlying_table_info listed below)\n"
                f"{self.underlying_table_info}"
            )

    def get_underlying_table(self, id=None) -> DataTable:
        """Returns the underlying DataTable from the datasource by id.

        Parameters
        ----------
        id (optional): The ID of the table to get

        Raises
        ------
        ValueError if an id is not provided and there are more than 1 logical table in the datasource.
        """
        if id:
            return DataTable(self.getLogicalTableDataAsync(id))

        tables = self.getLogicalTablesAsync()
        if len(tables) > 1:
            raise exceptions.MultipleTablesException(
                "More than one logical table exists in the datasource so you need to specify the underlying table\n"
                "id using the 'id' argument.\n"
                'A list of (caption, table_id) can be found using the "underlying_table_info" property\n'
                "(result of self.underlying_table_info listed below)\n"
                f"{self.underlying_table_info}"
            )
        table_id = tables[0].id
        return DataTable(self.getLogicalTableDataAsync(table_id))

    def get_underlying_data(self, id=None):
        """Return the underlying data as a list of dictionaries.

        Parameters
        ----------
        id (optional): The ID of the table to get. This is requried if there are more than one underlying logical tables.
        """
        return self.get_underlying_table(id).get_records()

    @property
    def underlying_table_info(self):
        """Information on each table contained in the datasource.

        type : :obj:`list` of :obj:`tuple` (caption, id)

        "caption" is the name of the table in the Tableau UI, while "id" is the unique
        identifier for the table in Tableau, which can be used in functions like "get_underlying_table".

        Example
        -------
        >>> ds = self.worksheet.datasources[0]
        >>> ds.underlying_table_info
        [('Orders', 'Orders_6D2EF74F348B46BDA976A7AEEA6FB5C9'), ('People', 'People_37AF7429D04E4916914EED91681E5975'), ('Returns', 'Returns_11818460B7524AB795D23E763C65D6BC')]
        """
        return [(table.caption, table.id) for table in self.getLogicalTablesAsync()]

    def refresh(self):
        """
        Refreshes data source
        """
        # Can we make this happen without blocking? Not sure how, call_async or something?
        # Yes, anvil labs has a non-blocking module which would handle that.
        self._proxy.refreshAsync()


class Worksheet(TableauProxy):
    """Represents an individual Tableau worksheet that exists in a Tableau dashboard. Contains methods to
    get underlying data, filters, and parameters.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html>` and accessed through the ``Worksheet`` object's ``._proxy`` attribute.
    """

    @property
    def columns(self):
        """Returns the columns of the worksheet as a dictionary with ``{colname: coltype}``.

        :type: dict

        Example
        -------
        >>> ws = self.dashboard.get_worksheet('Sales Summary')
        >>> ws.columns
        {'Customer Name': 'string', 'AGG(Profit Ratio)': 'float', 'SUM(Profit)': 'float', 'SUM(Sales)': 'float'}
        """
        return _clean_columns(self.getSummaryColumnsInfoAsync())

    def _coalesce_data(self, data, collapse_measures, method_name):
        """
        Returns the records from multiple data tables.
        """
        datatables = [DataTable(table) for table in data]
        if len(datatables) > 1:
            print(
                f"NOTE: {method_name} is returning data from multiple logical tables. \n"
                "The returned list will likely have different keys from element to element."
            )
        return list(
            itertools.chain(*[dt.get_records(collapse_measures) for dt in datatables])
        )

    def get_selected_marks(self, collapse_measures=False):
        """The data for the marks which are currently selected on the worksheet.
        If there are no marks currently selected, an empty list is returned.

        Parameters
        ----------
        collapse_measures : bool
            Whether or not to try and collapse records on worksheets that use
            measure names / measure values. This often happens when getting summary
            data for dual axis visualizations.

        Returns
        --------
        records : list
            Data for the currently selected marks on the worksheet
        """
        data = self._proxy.getSelectedMarksAsync()["data"]
        return self._coalesce_data(data, collapse_measures, "get_selected_marks")

    def get_highlighted_marks(self, collapse_measures=False):
        """The data for the marks which are currently highlighted on the worksheet.
        If there are no marks currently highlighted, an empty list is returned.

        Parameters
        ----------
        collapse_measures : bool
            Whether or not to try and collapse records on worksheets that use
            measure names / measure values. This often happens when getting summary
            data for dual axis visualizations.

        Returns
        --------
        :obj:`list` of :obj:`dicts`
        """
        data = self._proxy.getHighlightedMarksAsync()["data"]
        return self._coalesce_data(data, collapse_measures, "get_highlighted_marks")

    def get_underlying_data(self, table_id=None):
        """Get the underlying data as a list of dictionaries (records).

        If more than one "underlying table" exists, the table id must be specified.

        Parameters
        ----------
        table_id : str
            The table id for which to get the underlying data. Required if more than one logical table exists.

        Returns
        -------
        :obj:`list` of :obj:`dicts`

        Raises
        -------
        ValueError
            If more than one table_id exists, then a table must be specified.
        """
        ws = self._proxy

        if table_id is None:
            # we need to get the only underlying table id.
            tables = ws.getUnderlyingTablesAsync()
            if len(tables) > 1:
                raise ValueError(
                    "More than one underlying table exists."
                    "Need to specify the underlying table. "
                    "You can get the underlying table information using the "
                    "underlying_table_info property. "
                    f"\nValid tables: {self.underlying_table_info}"
                )

            table_id = tables[0].id

        datatable = DataTable(ws.getUnderlyingTableDataAsync(table_id))
        return datatable.get_records()

    def get_summary_data(self, ignore_selection=True, collapse_measures=False):
        """Returns the summary data from a worksheet.

        Parameters
        ---------
        ignore_selection : bool
            Whether or not to ignore the selected marks when getting summary data.

        collapse_measures : bool
            Whether or not to try and collapse records on worksheets that use
            measure names / measure values. This often happens when getting summary
            data for dual axis visualizations.

        Returns
        ---------
        :obj:`list` of :obj:`dict`
        """
        datatable = DataTable(
            self._proxy.getSummaryDataAsync({"ignoreSelection": ignore_selection})
        )
        return datatable.get_records(collapse_measures)

    def select_marks(self, dimension, selection_type="select-replace"):
        """Selects the marks and returns them.

        This version selects by value, using the SelectionCriteria interface.

        Note that this doesnt work on scatter plots.

        Parameters
        ----------
        dimension : dict or list of dict

        optional selection_type : str
            The type of enum to be applied to the marks

        Example
        ----------

        If ``Bar Chart`` is a standard Tableau bar chart:

        >>> bc = self.dashboard.get_worksheet('Bar Chart')
        >>> bc.select_marks({'Region': 'Asia'})

        And the Bar with the "Asia" Region will become selected.
        """
        selection_enums = ("select-replace", "select-add", "select-remove")
        if selection_type not in selection_enums:
            raise ValueError(
                f"Invalid selection type '{selection_type}'. "
                f"Valid values: {', '.join(selection_enums)}"
            )
        if not isinstance(dimension, list):
            dimension = [dimension]
        selection = [
            {"fieldName": k, "value": [v]} for d in dimension for k, v in d.items()
        ]
        self._proxy.selectMarksByValueAsync(selection, selection_type)
        return self.get_selected_marks()

    def clear_selection(self):
        """Clears the current marks selection."""
        self._proxy.clearSelectedMarksAsync()

    @property
    def filters(self):
        """A list of all currently selected filters.


        Returns
        --------
        :obj:`list` of :obj:`Filter`
            The currently selected filters. Valid types of filters include:
                Categorical, Hierarchical, Range, RelativeDate
        """
        return [Filter._create_filter(f) for f in self._proxy.getFiltersAsync()]

    def get_filter(self, filter_name):
        """Returns information on a given selected filter.


        Parameters
        ----------
        filter_name : str
            Name of the filter

        Returns
        ----------
        specified_filter : FieldName
            The selected filter
        """
        specified_filter = [f for f in self.filters if f.field_name == filter_name]
        if not specified_filter:
            raise KeyError(
                f"No filter matching field_name {filter_name}. "
                f"Worksheet filters: {[f.field_name for f in self.filters]}"
            )

        specified_filter = specified_filter[0]
        return specified_filter

    def clear_filter(self, filter):
        """Resets existing filters on the given field.

        Parameters
        ----------
        filter : str or Filter
            The name or Filter Object of the field to clear filter on.
        """
        if isinstance(filter, Filter):
            filter = filter.field_name
        self._proxy.clearFilterAsync(filter)

    def _check_for_existing_filter(self, field_name, filter_type):
        """Prints a warning message if a filter on field_name already exists
        and is a different type than filter_type.

        Example
        -------
        Assume that a dashboard has a range filter on SUM(Profit):

        >>> ws = self.dashboard.get_worksheet('ProductView')
        >>> ws.apply_categorical_filter('SUM(Profit)', ['($606)', '($555)'])
        # Retrieving the filter raises an error, and the worksheet will show both a categorical
        # AND a range filter applied to it.
        >>> ws.get_filter('SUM(Profit)').describe()
        ExternalError: Error: internal-error: Missing output parameter: categoricalDomain
        """
        try:
            existing_filter = self.get_filter(field_name)
            if existing_filter.filter_type != filter_type:
                print(
                    f"Note: There is already a {existing_filter.filter_type} filter on {field_name}.\n"
                    f"Applying a {filter_type} filter with apply_{filter_type}_filter will potentially put the dashboard in an unstable state."
                )
        except KeyError:
            pass

    def apply_categorical_filter(self, field_name, values, update_type="replace"):
        """Applies the list of provided categorical filter values.

        Parameters
        ----------
        field_name : str
            Name of the field in Tableau

        values : list
            List of values to filter on

        optional update_type : str
            The type of update to be applied to the filter
        """
        self._check_for_existing_filter(field_name, "categorical")
        if not isinstance(values, list):
            values = [values]

        self._proxy.applyFilterAsync(field_name, values, update_type)

    def apply_range_filter(self, field_name, min, max):
        """Applies a range filter.

        Parameters
        ----------
        field_name : str
            Name of the field in Tableau

        min : float
            Minimum value for the filter

        max : float
            Maximum value for the filter
        """
        self._check_for_existing_filter(field_name, "range")
        self._proxy.applyRangeFilterAsync(
            field_name, {"min": _to_js_date(min), "max": _to_js_date(max)}
        )

    @property
    def parameters(self):
        """All the Tableau parameters that are used in this workbook.

        :type: :obj:`list`
        """
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        """Getting the parameter information for the given parameter name.

        Parameters
        ----------
        parameter_name : str
            Name of the desired parameter name

        Returns
        ---------
        :obj:`Parameter`

        Raises
        ---------
        KeyError
            If no matching parameter is found.
        """
        param_js = self._proxy.findParameterAsync(parameter_name)
        if not param_js:
            raise KeyError(
                f"No matching parameter found for {parameter_name}. "
                f"Parameters on Dashboard: {[p.name for p in self.parameters]}"
            )
        else:
            return Parameter(param_js)

    @property
    def datasources(self) -> list[Datasource]:
        """The data sources for this worksheet.

        Returns
        ----------
        data_sources : :obj:`list` of :obj:`Datasource`
            The primary data source and all of the secondary data sources for this
            worksheet.
        """
        return [Datasource(ds) for ds in self._proxy.getDataSourcesAsync()]

    @property
    def underlying_table_info(self):
        """Returns information on each table contained in the datasource.

        "caption" is the name of the table in the Tableau UI, while "id" is the unique
        identifier for the table in Tableau.

        type : :obj:`list` of :obj:`tuple` (caption, id)
        """
        return [
            (table.caption, table.id)
            for table in self._proxy.getUnderlyingTablesAsync()
        ]

    @function_type_hint.event_handler_enum(
        selection_changed=EventHandler(event_type=MarksSelectedEvent),
        filter_changed=EventHandler(event_type=FilterChangedEvent),
        parameter_changed=EventHandler(event_type=ParameterChangedEvent),
    )
    def register_event_handler(self, event_type, handler):
        """Register an event handling function for a given event type.

        You can register ``selection_changed`` and ``filter_changed`` events at the
        worksheet level.

        The handler function will be called when selections or filters (depending on ``event_type``) are changed in
        the worksheet.

        If filters in another worksheet affect the filter on this worksheet, this event
        will be called.

        The function you pass to ``register_event_handler`` must take an event instance as an argument (either a :obj:`ParameterChangedEvent` or :obj:`FilterChangedEvent` depending on ``event_type``).

        Parameters
        ----------
        event_type : 'selection_changed', 'filter_changed', 'parameter_changed'
            The event type to register the handler for.
        handler : function
            The function to call when the event is triggered. ``handler`` must take an event instance as an argument.
        """
        session = _Tableau.session()
        if event_type in [
            "selection_changed",
            "filter_changed",
            events.SELECTION_CHANGED,
            events.FILTER_CHANGED,
        ]:
            session.register_event_handler(event_type, handler, self)

        elif event_type in ["parameter_changed", events.PARAMETER_CHANGED]:
            for p in self.parameters:
                p.register_event_handler(handler)

        else:
            raise NotImplementedError(
                "You can only set selection_changed, filter_changed, or "
                f"parameter_changed from the Sheet object. You tried: {event_type}"
            )

    def unregister_event_handler(self, handler, event_type=None):
        if isinstance(event_type, str):
            try:
                event_type = events.event_types[event_type]
            except KeyError:
                raise KeyError(
                    f"Unrecognized event_type {event_type}. "
                    f"Valid events: {list(events.event_types.keys())}"
                )

        session = _Tableau.session()
        session.unregister_event_handler(self, handler, event_type)

    def unregister_all_event_handlers(self):
        session = _Tableau.session()
        session.unregister_all_event_handlers(self)
        for p in self.parameters:
            p.unregister_all_event_handlers()

    def __str__(self):
        return f"Worksheet named '{self.name}'"


class Settings(TableauProxy):
    """Dict-like representation of Tableau Settings. Settings are persisted in the workbook between sessions but can only be modified
    in authoring mode.

    Typically accessed through dashboard.settings.

    Settings behaves like a dict and can be accessed and set through standard dict notation:

    >>> settings = get_dashboard().settings
    >>> my_setting = settings['my_setting']
    >>> settings['my_new_setting'] = 'a_new_value'

    Most of the standard dict methods are implemented. ``pop`` is not implemented; settings cannot be changed when
    the dashboard is not in 'author' mode, so probably, this isn't what you want.

    Non-standard dict methods

    * :obj:`Settings.delete`: Removes that key from settings if it exists.

    * :obj:`Settings.setdefaults`: Similar to ``setdefault`` and ``update``, where all of the keys in the passed dictionary are updated only if they don't exist. This avoids repeated writes to the dashboard if many defaults need setting at once.


    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/settings.html>` and accessed through the ``Setting`` object's ``._proxy`` attribute.
    """

    def _setkey(self, key, value):
        if key is None:
            raise KeyError("'None' is not a valid key for settings.")
        elif not isinstance(key, str):
            raise KeyError(
                f"Key {key} is not a string. Only string keys are allowed in Settings."
            )

        if not any(
            [
                isinstance(value, t)
                for t in [int, float, str, dict, list, tuple, dt.date, dt.datetime]
            ]
        ):
            print(
                f"Warning: Settings {key} (with value {value}) is of type {type(value)}! Settings persisted in the "
                f"workbook are stored as JSON. Make sure the serialization and deserialization "
                f"of {key} occurs as you expect. Otherwise, consider converting to a simple object type."
            )

        self._proxy.set(key, _jsonify(value))

    def keys(self):
        """Identical to dict.keys()."""
        return self.dict().keys()

    def values(self):
        """Identical to dict.values()."""
        return self.dict().values()

    def items(self):
        """Identical to dict.items()."""
        return self.dict().items()

    def get(self, item, default=None):
        """Identical to dict.get(key, default_value)."""
        value = _dejsonify(self._proxy.get(item))
        return value if value is not None else default

    def __getitem__(self, item):
        if item not in self.keys():
            raise KeyError(f"Setting {item} wasn't found.")
        value = self.get(item)
        return value

    def __setitem__(self, item, value):
        self._setkey(item, value)
        self._proxy.saveAsync()

    def __len__(self):
        return len(self.keys())

    def __contains__(self, item):
        return item in self.keys()

    def __delitem__(self, item):
        # A bug exists in the Extension API (or is introduced by the anvil.js framework)
        # where keys set to an empty string cannot be deleted.
        if self.get(item) == "":
            self._proxy.set(item, "TO BE DELETED")
        self._proxy.erase(item)
        self._proxy.saveAsync()

    def update(self, update_dict):
        """Identical to dict.update(dict). This is a little more efficient than updating many keys
        one at a time, since setting each key requires writing to the dashboard."""
        for k, v in update_dict.items():
            self._setkey(k, v)
        self._proxy.saveAsync()

    def delete(self, key):
        """This deletes the key from settings.

        Parameters
        ----------
        key : str
            They key to be deleted.
        """
        self.__delitem__(key)

    def clear(self):
        """Identical to dict.clear()."""
        for key in list(self.keys()):
            self.delete(key)

    def dict(self):
        """Converts settings to a dictionary.

        Returns
        -------
        settings_dict : a dictionary copy of settings.
            Note that this makes a copy of settings. Changing settings_dict will not affect
            the settings in the dashboard.
        """
        settings_dict = dict(self._proxy.getAll())
        settings_dict = {k: _dejsonify(v) for k, v in settings_dict.items()}
        return settings_dict

    def __str__(self):
        return f"Tableau Workbook Settings: {self.dict()}"

    def __repr__(self):
        return str(self.dict())

    def setdefault(self, key, default_value=""):
        """Identical to dict.setdefault(key, default_value)."""
        if key in self.keys():
            return self[key]

        else:
            self[key] = default_value
            return default_value

    def setdefaults(self, defaults_dict):
        """Sets all the defaults in the defaults_dict provided. If a key does not
        exist in settings, it is set to the default provided; otherwise, the value is not changed.

        Parameters
        ----------
        defaults_dict : dict
            Key value pairs representing the setting key and the default value to use
            if the key does not exist in settings.
        """
        initial_keys = list(self.keys())
        for k, v in defaults_dict.items():
            if k not in initial_keys:
                self._setkey(k, v)

        self._proxy.saveAsync()

    def __bool__(self):
        return bool(self.dict())

    def __iter__(self):
        return iter(self.dict())


class Dashboard(TableauProxy):
    """This represents the Tableau dashboard within which the extension is embedded. Contains
    methods to retrieve parameters, filters, and data sources.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html>` and accessed through the ``Dashboard`` object's ``._proxy`` attribute.
    """

    identifier = "id"

    def __init__(self, proxy):
        super().__init__(proxy)
        self.refresh()

    def refresh(self):
        """Refreshes the worksheets in the live Tableau Instance."""
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

    def __getitem__(self, idx):
        return self.get_worksheet(idx)

    def __str__(self):
        return (
            f"Dashboard named '{self.name}' with {len(self.worksheets)} worksheet(s)."
        )

    @property
    def name(self):
        """The name of the Tableau dashboard (as it appears in the Tableau UI).

        :type: :obj:`str`
        """
        if self._proxy is None:
            return None
        return self._proxy.name

    @property
    def worksheets(self):
        """All worksheets within the Tableau dashboard.

        :type: :obj:`list` of :obj:`Worksheet`
        """
        return [Worksheet(ws._proxy) for ws in self._worksheets.values()]

    def get_worksheet(self, sheet_name):
        """Gets a dashboard worksheet by name.

        Parameters
        ----------
        sheet_name : str
            Name of the worksheet.

        Returns
        ----------
        :obj:`Worksheet`

        Raises
        ----------
        KeyError
            If no matching worksheet is found
        """
        try:
            return self._worksheets[sheet_name]
        except KeyError:
            raise KeyError(
                f"Worksheet {sheet_name} doesn't exist. "
                f"Worksheets in dashboard: {list(self._worksheets.keys())}"
            )

    @property
    def filters(self):
        """All filters within all worksheets in the Tableau dashboard.

        :type: :obj:`list` of :obj:`Filter`
        """
        filters = []
        for ws in self.worksheets:
            filters.extend(ws.filters)
        return filters

    @property
    def parameters(self):
        """All parameters within the Tableau dashboard.

        :type: :obj:`list` of :obj:`Parameter`
        """
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        """Returns the parameter matching the provided parameter_name.

        Parameters
        ----------
        parameter_name : str
            Name of the parameter

        Returns
        --------
        :obj:`Parameter`

        Raises
        --------
        KeyError
            If no matching parameter is found
        """
        param_js = self._proxy.findParameterAsync(parameter_name)
        if not param_js:
            raise KeyError(
                f"No matching parameter found for {parameter_name}. "
                f"Parameters on Dashboard: {[p.name for p in self.parameters]}"
            )
        else:
            return Parameter(param_js)

    @property
    def datasources(self):
        """All data sources in the Tableau dashboard.

        .. Note that the Workbook method getAllDataSourcesAsync appears unreliable, so we iterate through worksheets to gather all data sources.

        :type: :obj:`list` of :obj:`Datasource`
        """
        known_ids = set()
        all_datasources = list()
        for ws in self.worksheets:
            for ds in ws.datasources:
                uid = (ds.id, ds.name)
                if uid in known_ids:
                    continue
                else:
                    known_ids.add(uid)
                    all_datasources.append(ds)

        return [Datasource(ds._proxy) for ds in all_datasources]

    def get_datasource(self, datasource_name):
        """Returns a Tableau data source by its name (case sensitive).

        Parameters
        -----
        datasource_name : str
            Name of the data source

        Returns
        -----
        :obj:`Datasource`

        Raises
        -----
        KeyError
            If no data source matching `datasource_name` is found.
        """
        # FIXME: Autocomplete fails to recognize return type as Datasource
        ds = [ds for ds in self.datasources if ds.name == datasource_name]
        if not ds:
            raise KeyError(
                f"No matching datasource found for {datasource_name}. "
                f"Datasources in Dashboard: {[ds.name for ds in self.datasources]}"
            )
        else:
            return Datasource(ds[0]._proxy)

    def get_datasource_by_id(self, datasource_id):
        """Returns a Tableau data source object by id.

        Parameters
        ----
        datasource_id : str
            ID of the data source

        Returns
        -----
        :obj:`Datasource`

        Raises
        -----
        KeyError
            If no datasource matching `datasource_id` is found.
        """
        # FIXME: Autocomplete fails to recognize return type as Datasource
        ds = [ds for ds in self.datasources if ds.id == datasource_id]
        if not ds:
            raise KeyError(
                f"No matching datasource found for {datasource_id}. "
                f"Datasource IDs in Dashboard: {[ds.id for ds in self.datasource_id]}"
            )
        else:
            return Datasource(ds[0]._proxy)

    def refresh_data_sources(self):
        """Refresh all data sources for the Tableau dashboard.

        This call has the same functionality as clicking the Refresh option on a
        data source in Tableau.

        """
        for ds in self.datasources:
            ds.refresh()

    @function_type_hint.event_handler_enum(
        selection_changed=EventHandler(event_type=MarksSelectedEvent),
        filter_changed=EventHandler(event_type=FilterChangedEvent),
        parameter_changed=EventHandler(event_type=ParameterChangedEvent),
    )
    def register_event_handler(self, event_type, handler):
        """Register an event handling function for a given event type.

        You can register ``selection_changed`` and ``filter_changed`` events at the
        dashboard level.

        Selections or filters changed anywhere in the dashboard will be handled.

        Parameters
        ----------
        event_type : str
            The event type to register the handler for.
        handler : function
            The function to call when the event is triggered.
        """
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
                "You can only set selection_changed, filter_changed, or "
                f"parameter_changed from the Dashboard object. You passed: {event_type}"
            )

    def unregister_all_event_handlers(self):
        for w in self.worksheets:
            w.unregister_all_event_handlers()
        for p in self.parameters:
            p.unregister_all_event_handlers()

    @property
    def settings(self):
        """The current dashboard settings. Dashboard settings provide a simple way to persist
        configuration variables in the workbook. Using Settings you can make your Extensions
        flexible and adaptable between  workbooks. Settings cannot be changed unless the
        Dashboard is opened in edit-mode or through Tableau Desktop.

        :type: :obj:`Settings` object.
        """
        return Settings(tableau.extensions.settings)

    @property
    def author_mode(self):
        """Whether or not the dashboard in which the Extension is embedded is in author-mode.
        Dashboards are in author-mode when web-authoring or opened in Tableau Desktop.

        Settings can only be changed or updated when the workbook is in author_mode.

        :type: :obj:`bool`
        """
        return tableau.extensions.environment.mode == "authoring"


class _Tableau:
    """The main interface to Tableau.

    Creating an instance of class this will initialize a tableau session and make
    available a Dashboard instances with its related objects and methods.

    Attributes
    ----------
    dashboard : Dashboard
    timeout : int
        The number of seconds to wait for the session to be initialized.
    """

    _session = None

    @classmethod
    def session(cls):
        """Constructor method for the Tableau class.

        Returns
        -------
        Tableau
        """
        if cls._session is None:
            cls._session = _Tableau()
            cls._session.available
        return cls._session

    def __init__(self):
        if self._session is not None:
            raise ValueError("You've already started a session. Use Tableau.session().")

        self.timeout = None
        self.event_type_mapper = _EventTypeMapper()
        self._proxy = tableau.extensions
        self.callbacks = {}
        self.dashboard = Dashboard(tableau.extensions.dashboardContent.dashboard)

    @property
    def available(self):
        """Whether the current session is yet available."""
        return self.dashboard._proxy is not None

    def register_event_handler(self, event_type, handler, targets):
        """Register an event handling function for a given event type.

        Parameters
        ----------
        event_type : str
            The event type to register the handler for.
            TODO: Valid values are selection_changed, filter_changed, or parameter_changed.
        handler : function
            The function to call when the event is triggered.
        targets : list
            The list of targets to register the handler for.
        """
        if not self.available:
            raise ValueError("No tableau session is available")

        if isinstance(event_type, str):
            try:
                event_type = events.event_types[event_type]
            except KeyError:
                raise KeyError(
                    f"Unrecognized event_type {event_type}. "
                    f"Valid events: {list(events.event_types.keys())}"
                )

        try:
            _ = len(targets)
        except TypeError:
            targets = (targets,)

        reporting_handler = report_exceptions(handler)
        if event_type == events.FILTER_CHANGED:
            reporting_handler = _suppress_duplicate_events(reporting_handler)
        tableau_event = self.event_type_mapper.tableau_event(event_type)

        def wrapper(event):
            wrapped_event = self.event_type_mapper.proxy(event)
            reporting_handler(wrapped_event)

        for target in targets:
            identifier = (target.__class__, target.id, handler, event_type)
            self.callbacks[identifier] = target._proxy.addEventListener(
                tableau_event, wrapper
            )

    def unregister_event_handler(self, target, handler, event_type=None):
        if event_type is not None:
            identifier = (target.__class__, target.id, handler, event_type)
        else:
            identifiers = [
                k
                for k in self.callbacks
                if target.__class__ == k[0] and target.id == k[1] and handler == k[2]
            ]
            if len(identifiers) > 1:
                raise ValueError(
                    "Handler has multiple registrations. Specify the event type"
                )
            identifier = identifiers[0]
        self.callbacks.pop(identifier)()

    def unregister_all_event_handlers(self, target):
        identifiers = [
            k for k in self.callbacks if target.__class__ == k[0] and target.id == k[1]
        ]
        for identifier in identifiers:
            self.callbacks.pop(identifier)()


class _EventTypeMapper:
    def __init__(self):
        self._tableau_event_types = None
        self._proxies = None
        self._tableau_event_types = {
            events.FILTER_CHANGED: "filter-changed",
            events.PARAMETER_CHANGED: "parameter-changed",
            events.SELECTION_CHANGED: "mark-selection-changed",
        }
        self._proxies = {
            "filter-changed": FilterChangedEvent,
            "mark-selection-changed": MarksSelectedEvent,
            "parameter-changed": ParameterChangedEvent,
        }

    def tableau_event(self, event_type):
        try:
            return self._tableau_event_types[event_type]
        except KeyError:
            raise ValueError(f"Unknown event type: {event_type}")

    def proxy(self, event):
        return self._proxies[event._type](event)
