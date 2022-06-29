Getting Started
==================

Let's build a Tableau Extension that shows the summary data of selected marks when a user clicks or selects part of the dashboard.

.. note:: This demo assumes the Anvil app has a single label called `label_1`.

Paste the following in the code section of the initial Anvil form

.. code-block:: python
    :linenos:

    # client_code/MainForm/__init__.py
    from ._anvil_designer import MainFormTemplate
    from anvil import *
    from tableau_extension.api import get_dashboard

    class MainForm(MainFormTemplate):
        def __init__(self, **properties):
            self.init_components(**properties)
            get_dashboard().register_event_handler('selection_changed', self.show_selections)

        def show_selections(self, event):
            self.label_1.text = str(event.worksheet.selected_records)

Above, we

* Get the current dashboard using :obj:`~client_code.api.get_dashboard` (line 9). 

    * This returns a Dashboard object that contains many useful things such as the datasources, filters, parameters, and worksheets. You can read more about those attributes here: :obj:`~client_code.model.proxies.Dashboard`

* Bind the `show_selections` function to the 'selection_changed' event. This function will run whenever a user changes the selection on the dashboard.

.. important:: The :obj:`~client_code.model.proxies.Dashboard.register_event_handler` method is the primary way to connect an action on a Tableau dashboard with Python code in the extension itself.


.. important:: TODO: Missing trex file download

..
    Change the following example, subject matter is not appropriate

.. dropdown:: Congrats, you now have a working Tableau extension!
    :open:

    .. image:: firstexample.gif
