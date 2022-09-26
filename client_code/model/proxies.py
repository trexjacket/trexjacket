import datetime as dt
import itertools

from anvil import tableau
from anvil.js import report_exceptions

from . import events
from .marks import Field, build_marks
from .utils import clean_record_key, native_value_date_handler

_event_cache = {}


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


class TableauProxy:
    identifier = None
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


class Datasource(TableauProxy):
    """Represents a Tableau data source. Only refreshing data sources is implemented with this API.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/datasource.html>` and accessed through the ``Datasource`` object's ``._proxy`` attribute.
    """

    def refresh(self):
        """
        Refreshes data source
        """
        # Can we make this happen without blocking? Not sure how, call_async or something?
        # Yes, anvil labs has a non-blocking module which would handle that.
        self._proxy.refreshAsync()

    @property
    def underlying_table_info(self):
        """Returns information on each table contained in the datasource.

        "caption" is the name of the table in the Tableau UI, while "id" is the unique
        identifier for the table in Tableau.

        type : :obj:`list` of :obj:`tuple` (caption, id)
        """
        return [
            (table.caption, table.id) for table in self._proxy.getLogicalTablesAsync()
        ]

    def get_underlying_records(self, table_id=None):
        """Get the underlying data from a datasource as a list of dictionaries.

        If more than one "underlying table" exists, the table id must be specified.

        Parameters
        --------
        table_id : str
          The table id for which to get the underlying data. Required if more than one logical
          table exists

        Returns
        --------
        :obj:`list` of :obj:`dicts`

        Example
        --------

        >>> self.dashboard = get_dashboard()
        >>> datasource = self.dashboard.get_datasource('Sample - Superstore')
        >>> recs = datasource.get_underlying_records('People_D73023733B004CC1B3CB1ACF62F4A965')
        >>> print(recs)

        [{'Regional Manager': 'Sadie Pawthorne'}, {'Regional Manager': 'Chuck Magee'}, {'Regional Manager': 'Roxanne Rodriguez'}, {'Regional Manager': 'Fred Suzuki'}]
        """
        ds = self._proxy

        if table_id is None:
            tables = ds.getLogicalTablesAsync()
            if len(tables) > 1:
                raise ValueError(
                    "More than one underlying table exists."
                    "Need to specify the underlying table. "
                    "You can get the underlying table information using the "
                    "underlying_table_info property. "
                    f"\nValid tables: {self.underlying_table_info}"
                )

            table_id = tables[0].id

        datatable = DataTable(ds.getLogicalTableDataAsync(table_id))

        return datatable.records


class Filter:
    """Represents a Tableau filter. Similar to parameters, you can use this class to read and change
    filter values.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/filter.html>` and accessed through the ``Filter`` object's ``._proxy`` attribute.
    """

    def __init__(self, proxy):
        self._proxy = proxy
        self.worksheet = None

    def __getattr__(self, name):
        return getattr(self._proxy, name)

    def __str__(self):
        return f"Filter: '{self.field_name}'"

    @property
    def serialized(self):
        return {"field_name": self.field_name, "values": self.applied_values}

    @property
    def field_name(self):
        """The name of the field being filtered.

        :type: str
        """
        return self._proxy.fieldName

    def _categorical_values(self):
        if self._proxy.isAllSelected:
            return self.domain

        try:
            return [v.nativeValue.getDate() for v in self.appliedValues]
        except AttributeError:
            return [v.nativeValue for v in self.appliedValues]

    def _range_values(self):
        try:
            return (
                self.minValue.nativeValue.getDate(),
                self.maxValue.nativeValue.getDate(),
            )
        except AttributeError:
            return (self.minValue.nativeValue, self.maxValue.nativeValue)

    def _relative_date_values(self):
        return self.periodType

    def _hierarchical_values(self):
        return "Hierarchical filter"

    @property
    def applied_values(self):
        """The current value(s) applied to the Filter.

        Returns
        ----------
        For categorical filters, returns a list of applied values
        For range filters, returns a tuple of (min, max)
        For relative date filters, returns period type
        For hierarchical filters, simply returns the string "Hierarchical filter"
        """
        if self.worksheet:
            self._proxy = self.worksheet.get_filter(self.field_name)._proxy

        handlers = {
            "categorical": self._categorical_values,
            "range": self._range_values,
            "relativeDate": self._relative_date_values,
            "hierarchical": self._hierarchical_values,
        }
        try:
            return handlers[self.filterType]()
        except KeyError:
            raise ValueError(
                f"Unrecognized filter type {self.filterType}. "
                f"Valid filter types: {list(handlers.keys())}"
            )

    @applied_values.setter
    def applied_values(self, new_values):
        """Replaces the set filter values.

        Parameters
        ----------
        new_values : :obj:`list` of :obj:`Filter`
            The new Filter values
        """
        self.set_filter_value(new_values)

    @property
    def domain(self):
        """The list of values that the filter can take.

        .. note::

            Only supported for categorical filters, see: https://github.com/Baker-Tilly-US/Tableau-Extension/issues/52

        :type: list
        """
        if self._proxy.filterType != "categorical":
            raise NotImplementedError(
                "domain is currently only available for categorical filters."
            )

        return [v.nativeValue for v in self._proxy.getDomainAsync("database").values]

    @property
    def relevant_domain(self):
        """The 'relevant' values for this specific filter.

        Returns
        --------
        domain : list of values
            The domain values that are relevant to the specified filter i.e. the domain
            is restricted by a previous filter
        """
        if self.worksheet:
            self._proxy = self.worksheet.get_filter(self.field_name)._proxy
        return [v.nativeValue for v in self._proxy.getDomainAsync("relevant").values]

    @property
    def filter_type(self):
        """The type of the Filter, one of (categorical | hierarchical | range | relative-date).

        :type: str
        """
        return self._proxy.filterType

    @property
    def field(self):
        """The field for the filter.

        :type: :obj:`~client_code.model.marks.Field`
        """
        return Field(self._proxy.getFieldAsync())

    def set_filter_value(self, new_values, method="replace"):
        """Replaces the list of provided categorical filter values.

        Parameters
        ----------
        new_values : :obj:`list`
            List of values to filter on

        optional update_type : str
            The type of update to be applied to the filter
        """
        self.worksheet.apply_filter(self.field_name, new_values, method)

    def clear_filter(self):
        """Resets the filter. Categorical filters are reset to 'All', range filters are reset to the full range."""
        self.worksheet.clear_filter(self.field_name)


class Parameter(TableauProxy):
    identifier = "id"

    """Represents a parameter in Tableau. Parameter values can be modified and read using this class.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/parameter.html>` and accessed through the ``Parameter`` object's ``._proxy`` attribute.
    """

    def refresh(self, parameter_changed_event=None):
        """Refreshes the object to reflect any changes in the dashboard."""
        self._proxy = Tableau.session().dashboard.get_parameter(self.name)._proxy

    def __str__(self):
        return f"Parameter: '{self.name}'"

    @property
    def serialized(self):
        try:
            return {"name": self.name, "value": self.value.getDate()}
        except AttributeError:
            return {"name": self.name, "value": self.value}

    @property
    def data_type(self):
        """The type of data this parameter holds. One of (bool | date | date-time | float | int | spatial | string).

        :type: str
        """
        return self._proxy.dataType

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
                    return float(val.formattedValue)
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

    @property
    def name(self):
        """The display name for this parameter.

        :type: str
        """
        return self._proxy.name

    @property
    def value(self):
        """The current value of the parameter."""
        self.refresh()
        return self._proxy.currentValue.nativeValue

    @value.setter
    def value(self, new_value):
        """Changes the DataValue representing the current value of the parameter.

        Parameters
        ----------
        new_value : DataValue
            DataValue representing the new value of the parameter.
        """
        self.change_value(new_value)

    def register_event_handler(self, handler):
        """Register an event handler that will be called whenever the parameter is changed.

        Note that the handler must take a ParameterChangedEvent instance as an argument.

        Parameters
        ----------
        handler : function
            Function that is called whenever the parameter is changed.
        """
        session = Tableau.session()
        session.register_event_handler(events.PARAMETER_CHANGED, handler, self)

    def unregister_event_handler(self, handler):
        session = Tableau.session()
        session.unregister_event_handler(self, handler, events.PARAMETER_CHANGED)

    def unregister_all_event_handlers(self):
        session = Tableau.session()
        session.unregister_all_event_handlers(self)


class Worksheet(TableauProxy):
    """Represents an individual Tableau worksheet that exists in a Tableau dashboard. Contains methods to
    get underlying data, filters, and parameters.

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html>` and accessed through the ``Worksheet`` object's ``._proxy`` attribute.
    """

    identifier = "name"

    def get_selected_records(self):
        """Gets the data for the marks which are currently selected on the worksheet.
        If there are no marks currently selected, an empty list is returned.

        Returns
        --------
        records : list
            Data for the currently selected marks on the worksheet
        """
        return self.selected_records

    @property
    def selected_records(self):
        """The data for the marks which are currently selected on the worksheet.
        If there are no marks currently selected, an empty list is returned.

        Returns
        --------
        records : list
            Data for the currently selected marks on the worksheet
        """
        data = self._proxy.getSelectedMarksAsync()["data"]
        datatables = (DataTable(table) for table in data)
        return list(itertools.chain(*[dt.records for dt in datatables]))

    @property
    def selected_marks(self):
        """Builds off of 'selected_records' method.

        Generates Marks by iterating through all records. (see 'build_marks in
        model.marks')

        Returns
        --------
        list : Marks
            A list of selected mark(s) on the worksheet
        """
        records = self.selected_records
        return build_marks(records)

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

    def get_underlying_records(self, table_id=None):
        """Get the underlying worksheet data as a list of dictionaries (records).

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
        return datatable.records

    def get_summary_records(self, ignore_selection=True):
        """Returns the summary data from a worksheet.

        Parameters
        ---------
        ignore_selection : bool
            Whether or not to ignore the selected marks when getting summary data

        Returns
        ---------
        :obj:`list` of :obj:`dict`
        """
        datatable = DataTable(
            self._proxy.getSummaryDataAsync({"ignoreSelection": ignore_selection})
        )
        return datatable.records

    def get_underlying_marks(self, table_id=None):
        """Get the underlying worksheet data as a list of Marks.

        If more than one "underlying table" exists, the table id must be specified.


        Parameters
        ----------
        table_id : str
            The table id for which to get the underlying data. Required if more than
            one logical table exists.

        Returns
        -------
        Mark
            list of Mark objects

        Raises
        -------
            ValueError: If more than one table_id exists, then a table must be specified.
        """
        records = self.get_underlying_records(table_id)
        return build_marks(records)

    @property
    def filters(self):
        """A list of all currently selected filters.


        Returns
        --------
        :obj:`list` of :obj:`Filter`
            The currently selected filters. Valid types of filters include:
                Categorical, Hierarchical, Range, RelativeDate
        """
        all_filters = [Filter(f) for f in self._proxy.getFiltersAsync()]
        for f in all_filters:
            f.worksheet = self
        return all_filters

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
        specified_filter.worksheet = self
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

    def apply_filter(self, field_name, values, update_type="replace"):
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
        if not isinstance(values, list):
            values = [values]

        print(
            f"applying filter async: {field_name} "
            f"filtered to {values} with method {update_type}"
        )
        self._proxy.applyFilterAsync(field_name, values, update_type)
        print("filter applied")

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
        self._proxy.applyRangeFilterAsync(field_name, {"min": min, "max": max})

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

        Assuming ``Bar Chart`` is a bar chart.

        >>> bc = self.dashboard.get_worksheet('Bar Chart')
        >>> bc.select_marks({'Region': 'Asia'})

        And you'll see that the Bar with Region = Asia becomes selected.
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
        return self.selected_records

    def clear_selection(self):
        """Clears the current marks selection."""
        self._proxy.clearSelectedMarksAsync()

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
    def datasources(self):
        """The data sources for this worksheet.

        Returns
        ----------
        data_sources : :obj:`list` of :obj:`Datasource`
            The primary data source and all of the secondary data sources for this
            worksheet.
        """
        return [Datasource(ds) for ds in self._proxy.getDataSourcesAsync()]

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
        session = Tableau.session()
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
        session = Tableau.session()
        session.unregister_event_handler(self, handler, event_type)

    def unregister_all_event_handlers(self):
        session = Tableau.session()
        session.unregister_all_event_handlers(self)
        for p in self.parameters:
            p.unregister_all_event_handlers()


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

    def __getitem__(self, idx):
        return self.get_worksheet(idx)

    def refresh(self):
        """Refreshes the worksheets in the live Tableau Instance."""
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

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
        return list(itertools.chain(*[ws.filters for ws in self.worksheets]))

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
    def name(self):
        """The name of the Tableau dashboard (as it appears in the Tableau UI).

        :type: :obj:`str`
        """
        if self._proxy is None:
            return None
        return self._proxy.name

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
                if ds.id in known_ids:
                    pass
                else:
                    known_ids.add(ds.id)
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
            return ds[0]

    def refresh_data_sources(self):
        """Refresh all data sources for the Tableau dashboard.

        This call has the same functionality as clicking the Refresh option on a
        data source in Tableau.

        """
        for ds in self.datasources:
            ds.refresh()

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


class Tableau:
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
            cls._session = Tableau()
            cls._session.available
        return cls._session

    def __init__(self):
        if self._session is not None:
            raise ValueError("You've already started a session. Use Tableau.session().")

        self.timeout = None
        self.event_type_mapper = EventTypeMapper()
        self._proxy = tableau.extensions
        self.callbacks = {}
        self.dashboard = Dashboard(tableau.extensions.dashboardContent.dashboard)

    @property
    def available(self):
        """Whether the current sesssion is yet available."""
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


class DataTable(TableauProxy):
    """Should be private

    .. note::

        A full listing of all methods and attributes of the underlying JS object can be viewed in the :bdg-link-primary-line:`Tableau Docs <https://tableau.github.io/extensions-api/docs/interfaces/datatable.html>` and accessed through the ``DataTable`` object's ``._proxy`` attribute.
    """

    @property
    def records(self):
        """The records in the data table.

        :obj:`list` of :obj:`dict`
        """
        keys = [c.fieldName for c in self._proxy.columns]
        return [
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

    def get_selected_records(self):
        """Returns the records that were selected in the worksheet.

        .. seealso::

            Example on the getting started guide :doc:`gettingstarted`
        """
        return self.worksheet.selected_records


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
        f = Filter(self._proxy.getFilterAsync())
        f.worksheet = self.worksheet
        return f

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


class EventTypeMapper:
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
