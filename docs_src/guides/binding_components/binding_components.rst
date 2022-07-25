Bind Anvil components to Tableau filters and parameters
----------

In order to keep Anvil components in sync with components on the dashboard (like filters and parameters), use the ``register_event_handler`` method of a :obj:`~client_code.model.proxies.Dashboard` object to set the properties of an Anvil component. In one sentence, we are saying: "Whenever the filter changes on the Tableau dashboard, go and upate this Anvil component".

For this how-to we'll assume there is a single Anvil form that contains some labels (prepended with ``lbl_``) and a single button with a function named ``btn_change_param_click`` bound to its click event. There is also a text box named ``text_box_1`` that will allow a user to input a new value for the parameter.

.. https://anvil.works/new-build/apps/5C66DY2E5OEFWOTZ/code/forms/BindComponents

.. code-block:: python
   :linenos:

   # Form code for a Form named "BindComponents"

   from ._anvil_designer import BindComponentsTemplate
   from anvil import tableau
   from tableau_extension.api import get_dashboard
   
   class BindComponents(BindComponentsTemplate):
     def __init__(self, **properties):
       self.init_components(**properties)
       self.dashboard = get_dashboard()
       
       # Register event handlers
       self.dashboard.register_event_handler('filter_changed', self.filter_change)
       self.dashboard.register_event_handler('parameter_changed', self.param_change)
       
       # "myparam" is the name of the parameter
       self.param = self.dashboard.get_parameter('myparam')
       
       # Get the first filter on the dashboard
       self.filter = self.dashboard.filters[0]
       
     def filter_change(self, event):
       """ This function runs whenever a Tableau filter changes. """
       self.lbl_filter_name.text = event.filter.field_name
       self.lbl_filter_value.text = self.filter.applied_values
       
     def param_change(self, event):
       """ This function runs whenever a Tableau parameter changes. """
       self.lbl_param_name.text = event.parameter.name
       self.lbl_param_value.text = self.param.value
       
     def btn_change_param_click(self, **event_args):
       """ This function is bound to the click event of the 'Apply' button and
       updates a parameter in Tableau from Anvil. """
       if self.text_box_1.text:
         self.param.value = self.text_box_1.text

The ``filter_changed`` and ``parameter_changed`` events are registered to methods that simply update text labels in Anvil. i.e.

.. WARNING: this is annoying to maintain

.. code-block:: python

    self.lbl_filter_name.text = event.filter.field_name


To update the Tableau parameter from Anvil, we assign the ``value`` property of the parameter in the click event handler (``btn_change_param_click``) for an Anvil button.


.. code-block:: python

    self.param.value = self.text_box_1.text
       
       
.. dropdown:: Here's what the extension should look like
    :open:

    .. image:: bindingdemo.gif

.. button-link:: https://anvil.works/build#clone:5C66DY2E5OEFWOTZ=N6AIAMZ6S2BXNTBPXWKTAIBM
   :color: primary
   :shadow:
   
   Click here to clone the Anvil used for this howto
   
Click :download:`here <component_binding.twb>` to download the Tableau workbook.
