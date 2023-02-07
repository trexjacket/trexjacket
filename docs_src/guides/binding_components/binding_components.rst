Bind Anvil components to Tableau filters and parameters
----------------------------------------------------------

Keeping Anvil components in sync with components on the dashboard is straight forward and simple using Anvil data bindings.

For this how-to, we'll assume that our Tableau dashboard has a single filter and a single parameter, and our Anvil extension has a text box and a multi-select drop down component.

Let's look at some form code:

.. https://anvil.works/new-build/apps/5C66DY2E5OEFWOTZ/code/forms/BindComponents

.. code-block:: python
  :linenos:

  from ._anvil_designer import BindComponentsTemplate
  from anvil import tableau

  from tableau_extension.api import get_dashboard

  class BindComponents(BindComponentsTemplate):
    def __init__(self, **properties):
      self.dashboard = get_dashboard()
      self.param = self.dashboard.get_parameter('myparam')
      self.filter = self.dashboard.filters[0]

      self.init_components(**properties)

      self.dashboard.register_event_handler('parameter_changed', self.refresh_data_bindings)
      self.dashboard.register_event_handler('filter_changed', self.refresh_data_bindings)

Notice that I've registered ``refresh_data_bindings`` to both the parameter_changed and filter_changed events. The only other step is to define the data bindings using the Anvil editor.

For the text box, bind the ``text`` property of the text box to ``self.param.value`` and enable write back.

.. image:: https://extension-documentation.s3.amazonaws.com/guides/binding_components/anvil_databinding.PNG

Checking the "Write back" box allows this assignment to go both ways and thus keeping Tableau and our Anvil extension in sync with each other.

The multi-select dropdown works similarly, but we'll need to bind the following:

- Drop down's ``items`` to ``self.filter.domain``
- Drop down's ``selected`` to ``self.filter.applied_values``, and enable write back

.. image:: https://extension-documentation.s3.amazonaws.com/guides/binding_components/ms_bindings.PNG

Once you've added the data bindings, your drop down and text box should be in sync with the Tableau dashboard!

.. dropdown:: Here's what the extension should look like
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/guides/binding_components/bindingdemo.gif

For more information on data bindings, see the `anvil docs here <https://anvil.works/docs/client/data-bindings>`_.


.. button-link:: https://anvil.works/build#clone:5C66DY2E5OEFWOTZ=N6AIAMZ6S2BXNTBPXWKTAIBM
   :color: primary
   :shadow:

   Click here to clone the Anvil used for this howto

Click :download:`here <component_binding.twb>` to download the Tableau workbook.
