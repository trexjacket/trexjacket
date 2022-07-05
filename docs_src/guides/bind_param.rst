Changing a parameter when a filter changes
=====

Use `get_parameter` with `register_event_handler`. 

.. code-block:: python
    :linenos:

    from ._anvil_designer import MainTemplate
    from anvil import *

    from tableau_extension import api

    class Main(MainTemplate):
      def __init__(self, **properties):
        self.init_components(**properties)

        self.dashboard = api.get_dashboard()
        self.dashboard.register_event_handler('filter_changed', self.modify_param)

      def modify_param(self, event):
        """ This method adds one to a parameter whenever a filter is changed. """
        param = self.dashboard.get_parameter('one')
        param.value += 1

      def primary_button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        param = self.dashboard.get_parameter('one')
        param.value = 500