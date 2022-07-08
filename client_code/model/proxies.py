import datetime as dt
import itertools
from time import sleep

import anvil
from anvil import tableau
from anvil.js import report_exceptions

from . import events
from .marks import Field, build_marks
from .utils import clean_record_key, loading_indicator, native_value_date_handler

_event_cache = {}


def _suppress_duplicate_events(event_handler):
    """Supress duplicate events is the .

    Private?
    #!

    Parameters
    ----------
    event_handler
        The action that needs to be handled.

    Returns
    ----------
    supressing_handler
        The supressed event handler.
    """

    def suppressing_handler(event):
        """
        #!
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
    """A base class for those requiring a Tableau proxy object."""

    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, name):
        return getattr(self._proxy, name)


class Datasource(TableauProxy):
    """Wrapper for a tableau Datasource

    https://tableau.github.io/extensions-api/docs/interfaces/datasource.html
    """

    def refresh(self):
        # Can we make this happen without blocking? Not sure how, call_async or something?
        self._proxy.refreshAsync()


class Filter:
    """Wrapper for a tableau Filter

    https://tableau.github.io/extensions-api/docs/interfaces/filter.html
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
        """The name of the field being filtered
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html#fieldname

        Returns
        --------
        field_name : Filter.FieldName
            The name of the field being filtered. Note that this is the caption as shown in the UI, and not the actual database field name.
        """
        return self._proxy.fieldName

    def _categorical_values(self):
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
        """Returns the current value applied to the Filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html

        Returns
        ----------
        filters : list of Filter
            The existing Filter values
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
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#applyfilterasync

        Parameters
        ----------
        new_values : list of Filter
            The new Filter values
        """
        self.set_filter_value(new_values)

    @property
    def domain(self):
        """Returns the domain for a Categorical Filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/categoricalfilter.html#getdomainasync

        Returns
        --------
        domain: list of values
            The domain for the selected Filter
        """
        return [v.nativeValue for v in self._proxy.getDomainAsync("database").values]

    @property
    def relevant_domain(self):
        """Returns the 'relevant' values for this specific filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/enums/tableau.filterdomaintype.html

        Returns
        --------
        domain : list of values
            The domain values that are relevant to the specified filter i.e. the domain is restricted by a previous filter
        """
        if self.worksheet:
            self._proxy = self.worksheet.get_filter(self.field_name)._proxy
        return [v.nativeValue for v in self._proxy.getDomainAsync("relevant").values]

    @property
    def filter_type(self):
        """Returns the type of Filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html#filtertype

        Returns
        --------
        type : filterType
            The type of the filter.
        """
        return self._proxy.filterType

    @property
    def field(self):
        """Returns a promise containing the field for the filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/categoricalfilter.html#getfieldasync

        Returns
        --------
        Promise : <field>
            a promise containing the field for the filter.
        """
        return Field(self._proxy.getFieldAsync())

    def set_filter_value(self, new_values, method="replace"):
        """Replaces the list of provided categorical filter values.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#applyfilterasync

        Parameters
        ----------
        new_values : list
            List of values to filter on

        optional update_type : str
            The type of update to be applied to the filter
        """
        self.worksheet.apply_filter(self.field_name, new_values, method)

    def clear_filter(self):
        """Resets the existing filters.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#clearfilterasync
        """
        self.worksheet.clear_filter(self.field_name)


class Parameter(TableauProxy):
    """Wrapper for a tableau Parameter

    https://tableau.github.io/extensions-api/docs/interfaces/parameter.html
    """

    def refresh(self, parameter_changed_event=None):
        """Refreshes the object to reflect any changes in the dashboard"""
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
    def domain(self):
        """Returns the allowable set of values this parameter can take.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#allowablevalues

        Returns
        --------
        allowableValues: ParameterDomainRestriction
            The allowable set of values this parameter can take.
        """
        return self.allowable_values()

    @property
    def data_type(self):
        """Returns the type of data this parameter holds.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#allowablevalues

        Returns
        --------
        dataType : DataType
            The type of data this parameter holds.
        """
        return self._proxy.dataType

    def allowable_values(self):
        """Returns the allowable set of values this parameter can take.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#allowablevalues

        Returns
        --------
        allowableValues: ParameterDomainRestriction
            The allowable set of values this parameter can take.
        """
        if self._proxy.allowableValues.type == 'all':
            raise ValueError(
                'allowable_values is only available for the "List" and "Range" allowable values. '
                'See https://tableau.github.io/extensions-api/docs/interfaces/parameterdomainrestriction.html '
                'for more information.'
            )

        return [d.nativeValue for d in self._proxy.allowableValues.allowableValues]

    def change_value(self, new_value):
        """Modifies this parameter and assigns it a new value.
        The new value must fall within the domain restrictions defined by allowableValues.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#changevalueasync

        Parameters
        ----------
        new_value : string | number | boolean | Date
            The new value to assign to this parameter. Note: For changing Date parameters, UTC Date objects are expected.
        """
        self._proxy.changeValueAsync(new_value)

    @property
    def name(self):
        """Returns the display name for this parameter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#name

        Returns
        ----------
        name : str
            The display name for this parameter.
        """
        return self._proxy.name

    @property
    def value(self):
        """Returns the DataValue representing the current value of the parameter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#currentValue

        Returns
        ----------
        currentValue: DataValue
            DataValue representing the current value of the parameter.
        """
        self.refresh()
        return self._proxy.currentValue.nativeValue

    @value.setter
    def value(self, new_value):
        """Changes the DataValue representing the current value of the parameter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#currentValue

        Parameters
        ----------
        new_value : DataValue
            DataValue representing the new value of the parameter.
        """
        self.change_value(new_value)

    def register_event_handler(self, handler):
        """Register an event handler that will be called whenever the parameter is changed.

        Note that the handler must take a ParameterChangedEvent instance as an argument.

        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#addeventlistener

        Parameters
        ----------
        handler : TableauEventHandlerFn
            The function which will be called when an event happens.
        """
        session = Tableau.session()
        self._listener = session.register_event_handler(
            events.PARAMETER_CHANGED, handler, self
        )

    def remove_event_handler(self):
        """Removes an event listener if a matching one is found. If no matching listener exists, the method does nothing.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html#removeeventlistener
        """
        if hasattr(self, "_listener") and self._listener:
            self._proxy.removeEventListener(events.PARAMETER_CHANGED, self._listener)
            self._listener = None


class Worksheet(TableauProxy):
    """Wrapper for a tableau Worksheet

    https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html
    """

    def get_selected_records(self):
        """Gets the data for the marks which are currently selected on the worksheet.
        If there are no marks currently selected, an empty list is returned.

        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getselectedmarksasync

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

        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getselectedmarksasync

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
        Generates Marks by iterating through all records. (see 'build_marks in model.marks')

        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/markscollection.html

        Returns
        --------
        list : Marks
            A list of selected mark(s) on the worksheet
        """
        records = self.selected_records
        return build_marks(records)

    def get_underlying_records(self, table_id=None):
        """Get the underlying worksheet data as a list of dictionaries (records).
        If more than one "underlying table" exists, the table id must be specified.

        See also:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getunderlyingtabledataasync

        Parameters
        ----------
        table_id : str
            The table id for which to get the underlying data. Required if more than one logical table exists.

        Returns
        -------
        records: list of dicts

        Raises:
        -------
        ValueError: If more than one table_id exists, then a table must be specified.
        """
        ws = self._proxy

        if table_id is None:
            # we need to get the only underlying table id.
            tables = ws.getUnderlyingTablesAsync()
            if len(tables) > 1:
                info = ", ".join([f"{t.caption} (id: {t.id})" for t in tables])
                raise ValueError(
                    "More than one underlying table exists. Need to specify the underlying table. "
                    "You can get the underlying table information using the get_underlying_tables method. "
                    f"Valid tables: {info}"
                )

            table_id = tables[0].id

        datatable = DataTable(ws.getUnderlyingTableDataAsync(table_id))
        return datatable.records

    def get_summary_records(self, ignore_selection=True):
        datatable = DataTable(
            self._proxy.getSummaryDataAsync({"ignoreSelection": ignore_selection})
        )
        return datatable.records

    def get_underlying_marks(self, table_id=None):
        """Get the underlying worksheet data as a list of Marks
        .
        If more than one "underlying table" exists, the table id must be specified.

        See also:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getunderlyingtabledataasync

        Parameters
        ----------
        table_id : str
            The table id for which to get the underlying data. Required if more than one logical table exists.

        Returns
        -------
        marks: list of Mark objects

        Raises:
        -------
        ValueError: If more than one table_id exists, then a table must be specified.
        """
        records = self.get_underlying_records(table_id)
        return build_marks(records)

    @property
    def filters(self):
        """Returns a list of all currently selected filters.
        For more informatio, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html

        Returns
        --------
        all_filters : list of Filters
            The currently selected filters. Valid types of filters include: Categorical, Hierarchical, Range, RelativeDate
        """
        all_filters = [Filter(f) for f in self._proxy.getFiltersAsync()]
        for f in all_filters:
            f.worksheet = self
        return all_filters

    def get_filter(self, filter_name):
        """Returns information on a given selected filter.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html#fieldname

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
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#clearfilterasync

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
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#applyfilterasync

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

    def select_marks(self, dimension, selection_type="select-replace"):
        """Selects the marks and returns them. This version selects by value, using the SelectionCriteria interface.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#selectmarksbyvalueasync

        Parameters
        ----------
        dimension :
        #!

        optional selection_type : str
            The type of enum to be applied to the marks
        """
        selection_enums = ("select-replace", "select-add", "select-remove")
        if selection_type not in selection_enums:
            raise ValueError(
                f"Invalid selection type '{selection_type}'. Valid values: {', '.join(selection_enums)}"
            )
        if not isinstance(dimension, list):
            dimension = [dimension]
        selection = [
            {"fieldName": k, "value": [v]} for d in dimension for k, v in d.items()
        ]
        self._proxy.selectMarksByValueAsync(selection, selection_type)

    def clear_selection(self):
        """Clears the current marks selection."""
        self._proxy.clearSelectedMarksAsync()

    @property
    def parameters(self):
        """A collection of all the Tableau parameters that are used in this workbook.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getparametersasync
        """
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        """Getting the parameter information for the given parameter name.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html

        Parameters
        ----------
        parameter_name : str
            Name of the desired parameter name

        Returns
        ---------
        parameter: Parameter instance
            Represents a parameter in Tableau and provides ways to introspect the parameter and change its values.
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
        """Gets the data sources for this worksheet.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/worksheet.html#getdatasourcesasync

        Returns
        ----------
        data_sources : list
            The primary data source and all of the secondary data sources for this worksheet.
        """
        return [Datasource(ds) for ds in self._proxy.getDataSourcesAsync()]

    def register_event_handler(self, event_type, handler):
        """Register an event handling function for a given event type.

        You can register 'selection_changed' and 'filter_changed' events at the worksheet level.
        The handler function will trigger when selections or filters are changed in the worksheet.

        If filters in one worksheet affect the filter on this worksheet, this event will be raised.

        The event handler must take a ParameterChangedEvent or FilterChangedEvent as an argument.

        For more information, see:
        https://tableau.github.io/extensions-api/docs/trex_events.html

        Parameters
        ----------
        event_type : str
            The event type to register the handler for.
        handler : function
            The function to call when the event is triggered.
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


class Dashboard(TableauProxy):
    """Wrapper for a tableau Dashboard

    https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html
    """

    def __init__(self, proxy):
        super().__init__(proxy)
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

    def __getitem__(self, idx):
        return self.get_worksheet(idx)

    def refresh(self):
        """Refreshes the worksheets in the live Tableau Instance."""
        self._worksheets = {ws.name: Worksheet(ws) for ws in self._proxy.worksheets}

    @property
    def worksheets(self):
        """Iterates through all of the worksheets in the dashboard and returns their info in a list.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html#worksheets

        Returns
        --------
        worksheets : list
            The collection of worksheets contained in the dashboard.

        #!
        """
        return list(self._worksheets.values())

    def get_worksheet(self, sheet_name):
        """Method that returns the specified worksheet from the active tableau instance.

        Parameters
        ----------
        sheet_name : str
            Name of the given worksheet.

        Returns
        ----------
        worksheet : Sheet.Dashboard.worksheet
            The desired worksheet
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
        """Property that returns the Class filters
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/filter.html

        Returns
        --------
        Filters : list of Filter
            Filters in Tableau that are used in this workbook.
        """
        return list(itertools.chain(*[ws.filters for ws in self.worksheets]))

    @property
    def parameters(self):
        """Property that returns the parameters in the Dashboard.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/dashboard.html#getparametersasync

        Returns
        --------
        Parameters : list of Parameter
            Parameters in Tableau that are used in this workbook.
        """
        return [Parameter(p) for p in self._proxy.getParametersAsync()]

    def get_parameter(self, parameter_name):
        """Returns the parameter matchin the provided parameter_name.

        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/parameter.html

        Parameters
        ----------
        parameter_name : str
            Name of the parameter

        Returns
        --------
        Parameters : list of Parameter
            Parameters in Tableau that are used in this workbook.
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
        """

        #!
        """
        if self.proxy is None:
            return None
        return self.proxy.name

    @property
    def datasources(self):
        """Returns all datasources in the dashboard.

        Note that the Workbook method getAllDataSourcesAsync appears unreliable, so we iterate
        through worksheets to gather all datasources.

        Returns:
        --------
        datasources : list of Datasource instances
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

        return all_datasources

    def get_datasource(self, datasource_name):
        ds = [ds for ds in self.datasources if ds.name == datasource_name]
        if not ds:
            raise KeyError(
                f"No matching datasource found for {datasource_name}. "
                f"Datasources in Dashboard: {[ds.name for ds in self.datasources]}"
            )
        else:
            return ds[0]

    def get_datasource_by_id(self, datasource_id):
        ds = [ds for ds in self.datasources if ds.id == datasource_id]
        if not ds:
            raise KeyError(
                f"No matching datasource found for {datasource_id}. "
                f"Datasource IDs in Dashboard: {[ds.id for ds in self.datasource_id]}"
            )
        else:
            return ds[0]

    def refresh_data_sources(self):
        """This call has the same functionality as clicking the Refresh option on a data source in Tableau.
        For more information, see:
        https://tableau.github.io/extensions-api/docs/interfaces/datasource.html#refreshasync
        """
        for ds in self.datasources:
            ds.refresh()

    def register_event_handler(self, event_type, handler):
        """Register an event handling function for a given event type.

        You can register 'selection_changed' and 'filter_changed' events at the dashboard level.
        Seletions or filters changed anywhere in the dashboard will be handled.

        For more information, see:
        https://tableau.github.io/extensions-api/docs/trex_events.html

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


class Tableau:
    """The main interface to Tableau.

    Creating an instance of class this will initialize a tableau session and make
    available a Dashboard instances with its related objects and methods.

    Attributes
    ----------
    dashboard : Dashboard
    """

    _session = None

    @classmethod
    def session(cls):
        """Constructor method for the Tableau class.

        Parameters
        ----------
        timeout : int
            The number of seconds to wait for the session to be initialized.

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
        self.dashboard = Dashboard(tableau.extensions.dashboardContent.dashboard)

    @property
    def available(self):
        """Whether the current sesssion is yet available"""
        return self.dashboard._proxy is not None

    def register_event_handler(self, event_type, handler, targets):
        """Register an event handling function for a given event type.

        Parameters
        ----------
        event_type : str
            The event type to register the handler for.
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

        handler = report_exceptions(handler)
        if event_type == events.FILTER_CHANGED:
            handler = _suppress_duplicate_events(handler)
        tableau_event = self.event_type_mapper.tableau_event(event_type)

        def wrapper(event):
            wrapped_event = self.event_type_mapper.proxy(event)
            handler(wrapped_event)

        handler_fn = None
        for target in targets:
            handler_fn = target._proxy.addEventListener(tableau_event, wrapper)

        return handler_fn


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
    """Wrapper for a tableau MarksSelectedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/marksselectedevent.html
    """

    @property
    def worksheet(self):
        """The Worksheet instance associated generating the Selection Event."""
        return Worksheet(self._proxy._worksheet)

    def get_selected_records(self):
        """Returns the records that were selected in the worksheet."""
        return self.worksheet.selected_records


class FilterChangedEvent(TableauProxy):
    """Wrapper for a tableau FilterChangedEvent

    https://tableau.github.io/extensions-api/docs/interfaces/filterchangedevent.html
    """

    def __hash__(self):
        return hash(self.fieldName)

    def __eq__(self, other):
        return self.fieldName == other.fieldName

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
