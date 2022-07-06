Bind a tableau categorical filter to an Anvil component
====

This guide will show how to build a repeating panel in Anvil that contains a row for each value selected in a categorical filter. It assumes that the Anvil app contains a single repeating panel named :code:`repeating_panel_1`.

.. code-block:: python
    :linenos:

    from ._anvil_designer import MainTemplate
    from anvil import *

    from tableau_extension import api

    class Main(MainTemplate):
      def __init__(self, **properties):
        self.init_components(**properties)

        self.dashboard = api.get_dashboard()
        self.dashboard.register_event_handler('filter_changed', self.show_values)

      def show_values(self, event):
        """ This method runs whenever a filter is changed. """
        filter_values = event.filter.applied_values

        print(f'{event.filter.field_name} filter was changed to {filter_values}.')

        self.repeating_panel_1.items = filter_values
        self.refresh_data_bindings()

As always, register an event handler to the dashboard object and set the callback function (:code:`show_values`). 

To retrieve the values of the filter that are currently applied, use :py:attr:`~client_code.model.proxies.Filter.applied_values`. In the callback function, set the repeating panel's :code:`repeating_panel_1.items` to the `applied_values` of the filter.