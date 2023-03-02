Chapter 4: Write our Client Code
================================

Now that we've written our server code, let's move back to the client side. In Chapter 1 we created the UI on the design slide of the form, to write our code we'll going to the aptly name Code tab.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image028.png

Add the following code to your form:

.. code-block:: python

    from trexjacket import api
    dashboard = api.get_dashboard()


First thing we will do is import the ``trexjacket`` library we setup all the way back in the dependency section. Then we are going to setup the dashboard object.

Create a dictionary to house the Opportunity attributes we want to change. We'll also call a function we haven't created yet ``self.reset()`` to clear the dictionary on screen load and refresh.

.. code-block:: python

    self.reset()
    self.new_dict = {
    	'StageName': None,
           'CloseDate': None,
           'Amount': None
        }


Call our get_opportunity_stages server function to fetch the list from Tableau. When calling server functions, we use the syntax ``anvil.server.call(function name', args, *kwargs)``

Then we want to stick those stages into a drop-down element in our screen. When you want to reference a screen element, we use ``self`` to reference the form class then the object name, ``self.object_name``.

We can assign a list to a drop-down property with items, ``self.drop_down_name.items``

`Anvil Docs on Drop Downs <https://anvil.works/learn/tutorials/database-backed-apps/chapter-3/30-populate-dropdown>`_

.. code-block:: python

    oppstages = anvil.server.call('opportunity_stages')
    self.drop_down_stage.items = oppstages

To finish off the init we're going to register the event handler. The event handler captures any selections the user makes in their dashboard so the extension can take action.

In our case, the event handler we give us the attributes of the selected Opportunity.

We want selection_changed and we'll call our event handler ``self.my_form_event_handler``.

All the code in this section goes before the line ``self.init_components(**properties)`` so it takes place before the form loads the UI.

.. code-block:: python

    dashboard.register_event_handler('selection_changed', self.my_form_event_handler)
    self.init_components(**properties)

Functions
---------

In this section we will create the functions for our class.

Event Handler

In the extension library the event is the thing that changes when a 'selection_changed' occurs. We want all the records from each change.

If something did change, we want to assign class variables with selected value, in our case the opportunity the user picked. We get the rest of the information using our server function get_opportunity.

The event handler closes with ``self.refresh_data_bindings()``. Refresh data binding will update any screen objects with the new values, you will want to do this after changing any bound variables. We will bind screen objects in a later section.

.. code-block:: python

    def my_form_event_handler(self, event):
        selected_value = event.get_selected_records()
        if selected_value:
          try:
            self.opp_name = selected_value[0]['Name']
            self.opp_ID = selected_value[0]['Opportunity ID']

            self.opportunity = anvil.server.call('get_opportunity',selected_value[0]['Opportunity ID'])
            self.opp_stage = self.opportunity['StageName']
            self.opp_date = self.opportunity['CloseDate']
            self.opp_amount = self.opportunity['Amount']
          except KeyError:
            pass
        else:
          self.reset()
        self.refresh_data_bindings()

Reset
------

We're adding reset to allow the user to clear the selected opportunity on page refresh or by clicking on a blank space in the dashboard.

.. code-block:: python

    def reset(self):
        self.opp_name = None
        self.opp_ID = None
        self.opp_stage = None
        self.opp_date = None
        self.opp_amount = None


Clear Changes
-------------

Clear changes will change all the selections in our ``new_dict`` to None, we call clear changes after we submit the API request to update the opportunity. This prevents the extension from sending unnecessary update requests.

.. code-block:: python

    def clear_changes(self):
        self.new_dict = {x: None for x in self.new_dict}

Buttons
--------

The remainder of our client code will handle screen events. Screen events occur when a user takes action on the UI like clicking a button or changing text in a text box.

You can find Events in the Container Properties. Go back to the Design view, look to the right side of the screen where you see Toolbox, then scroll to the bottom of the panel.

Depending on the screen component you've selected you you'll see different options like Show, Hide, Click, and Change.

`Anvil Documentation on Components and Events <https://anvil.works/docs/client/components>`_

Submit Changes

On the Design view select your Submit Changes button, scroll down on the right-side panel to the Container Properties section, click the blue button next to click.
This will open the split view and create the function ``button_submit_click``.

.. code-block:: python

    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/salesforce/image038.png

In the button submit click function we will add a call to the ``update_opportunity`` server function we created passing the ``self.opp_ID`` and ``self.new_dict`` as parameters.

If the return from the server function is True, we want clear our updates so we have a clean slate for any other changes.

Else, we'd like to create an alert letting the user know they haven't made any changes. Alerts generate a pop-up with content on the user's screen. Will we add a simple alert with some text.

`Anvil Documentation on Basic Components <https://anvil.works/docs/client/components/basic>`_

`Anvil Documentation on Alerts <https://anvil.works/docs/client/python/alerts-and-notifications>`_

.. code-block:: python

    def button_submit_click(self, **event_args):
        """This method is called when the button is clicked"""
        response = anvil.server.call('update_opportunity',self.opp_ID,self.new_dict)
        if response is True:
          self.clear_changes()
        else:
          alert('Please make a change before submitting.')


Pick from the Drop-Down
-----------------------

On the Design view select your Opportunity Stage drop-down, scroll down on the right-side panel to the Container Properties section, click the blue button next to change.

This will open the split view and create the function ``drop_down_stage_change``.

Assign the selected value from the drop down to the StageName variable in our new_dict and refresh the data bindings.

`Anvil Documentation on Basic Components <https://anvil.works/docs/client/components/basic>`_

.. code-block:: python

    def drop_down_stage_change(self, **event_args):
        """This method is called when an item is selected"""
        self.new_dict['StageName'] = self.drop_down_stage.selected_value
        self.refresh_data_bindings()

Change the Close Date
---------------------

On the Design view select your Close Date date picker, scroll down on the right-side panel to the Container Properties section, click the blue button next to change.

This will open the split view and create the function ``date_picker_1_change``.

Assign the date from the date picker to the CloseDate variable in our ``new_dict``, convert it to iso format, then refresh the data bindings.

`Anvil Documentation on Basic Components <https://anvil.works/docs/client/components/basic>`_

.. code-block:: python

    def date_picker_1_change(self, **event_args):
        """This method is called when the selected date changes"""
        self.new_dict['CloseDate'] = self.date_picker_1.date.isoformat()
        self.refresh_data_bindings()

Enter an Amount
---------------

On the Design view select your Amount text box, scroll down on the right-side panel to the Container Properties section, click the blue button next to change.

This will open the split view and create the function ``text_box_amount_change``. Go back to the Design view then Container Properties then copy past ``text_box_amount_change`` into the pressed_enter field as well.

Assign the selected value from the text box to the Amount variable in our new_dict, convert the text to an Integer.

Assign the same integer to the ``opp_amount`` variable.

Refresh the data bindings.

`Anvil Documentation on Basic Components <https://anvil.works/docs/client/components/basic>`_

.. code-block:: python

    def text_box_amount_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.new_dict['Amount'] = int(self.text_box_amount.text)
        self.opp_amount = int(self.text_box_amount.text)
        self.refresh_data_bindings()

Your form code should now look like this:
-----------------------------------------

.. code-block:: python
    :linenos:

    from ._anvil_designer import TB_FormTemplate
    from anvil import *
    from anvil import tableau
    import anvil.tables as tables
    import anvil.tables.query as q
    from anvil.tables import app_tables
    import anvil.server

    from trexjacket import api
    dashboard = api.get_dashboard()

    class TB_Form(TB_FormTemplate):
      def __init__(self, **properties):
        self.reset()
        self.new_dict = {
            'StageName': None,
            'CloseDate': None,
            'Amount': None
        }
        oppstages = anvil.server.call('opportunity_stages')
        self.drop_down_stage.items = oppstages
        dashboard.register_event_handler('selection_changed', self.my_form_event_handler)
        self.init_components(**properties)

      def reset(self):
          self.opp_name = None
          self.opp_ID = None
          self.opp_stage = None
          self.opp_date = None
          self.opp_amount = None

      def my_form_event_handler(self, event):
        selected_value = event.get_selected_records()
        if selected_value:
          try:
            self.opp_name = selected_value[0]['Name']
            self.opp_ID = selected_value[0]['Opportunity ID']
            self.opportunity = anvil.server.call('get_opportunity',selected_value[0]['Opportunity ID'])
            self.opp_stage = self.opportunity['StageName']
            self.opp_date = self.opportunity['CloseDate']
            self.opp_amount = self.opportunity['Amount']
          except KeyError:
            pass
        else:
          self.reset()
        self.refresh_data_bindings()

      def clear_changes(self):
        self.new_dict = {x: None for x in self.new_dict}

      def button_submit_click(self, **event_args):
          response = anvil.server.call('update_opportunity',self.opp_ID,self.new_dict)
          if True:
            self.clear_changes()
            self.refresh_data_bindings()
          else:
            alert('Please make a change before submitting.')

      def drop_down_stage_change(self, **event_args):
          self.new_dict['StageName'] = self.drop_down_stage.selected_value
          self.refresh_data_bindings()

      def date_picker_1_change(self, **event_args):
          self.new_dict['CloseDate'] = self.date_picker_1.date.isoformat()
          self.refresh_data_bindings()

      def text_box_amount_change(self, **event_args):
          self.new_dict['Amount'] = int(self.text_box_amount.text)
          self.opp_amount = int(self.text_box_amount.text)
