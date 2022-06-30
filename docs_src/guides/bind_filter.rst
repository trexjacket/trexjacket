Bind a tableau filter to an anvil component
====

Use `component.item` and `self.refresh_data_bindings()` to bind an anvil component to something like a filter or a parameter.

.. important::
    Need https://github.com/Baker-Tilly-US/Tableau-Extension/issues/42

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