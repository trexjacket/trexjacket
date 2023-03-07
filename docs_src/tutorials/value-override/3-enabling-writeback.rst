Chapter 3: Showing Overrides in the Dashboard
=============================================

In the last chapter we saved the overrides to an Anvil Data Table. In this chapter we'll connect our Tableau Dashboard to our Anvil Data Table so we can insert the overrides into a tooltip.

First we'll need to gather our database credentials from Anvil:

1. Click the Anvil X logo on the left sidebar

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/sidebar-x.PNG

2. Click "Enable" in Step 3.

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/enable-x.PNG

3. Note the "Server name", "Username", and "Password" fields

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/creds-x.PNG

Now that we have our credentials we'll need to add our Anvil Data Table as a new datasource to our Tableau dashboard:

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/add_data_source.gif

In Tableau:

1. Click "Data" in the top ribbon
2. Click "New Data Source"
3. In the "To a server" section, click "PostgreSQL"
4. Input the server name, username, and password from we copied from Anvil

Now that we have our Anvil data table as a datasource, let's add the override value to the tooltip:

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/add_tooltip.gif

1. Go to our worksheet (You should now see the ``overrides`` table from Anvil)
2. Click "Data" > "Edit Blend Relationship" in the top ribbon
3. Click "Custom" and then "Add..."
4. Set the "Primary data source field" to "State" and the "Secondary data source field" to "Id Value". Then click "OK" to close the dialogue
5. In the "Data" pane on the left, click "overrides (Anvil)", and drag the "Override Value" to the "Tooltip" box in the "Marks" section
6. Click the "tooltip" box and insert the "Override Value" to the tooltip.

.. admonition:: Test it out

    Hovering over each state should now show you the override value in the tooltip!

One last thing, we'll want to refresh this datasource whenever someone adds a new override. We can use the ``refresh`` method of our datasources to refresh them whenever an override is saved:

.. dropdown:: ``Homepage`` code
    :open:

    .. code-block:: python
      :linenos:
      :emphasize-lines: 47-48

      from ._anvil_designer import HomepageTemplate
      import anvil
      from anvil.tables import app_tables
      from datetime import datetime

      from trexjacket.api import get_dashboard
      from trexjacket import dialogs

      class Homepage(HomepageTemplate):
        def __init__(self, **properties):
          self.dashboard = get_dashboard()
          self.repeating_panel_1.items = app_tables.overrides.search()
          self.init_components(**properties)

        @property
        def worksheet(self):
          # Here we use the settings we configured to dynamically get the worksheet
          return self.dashboard.get_worksheet(self.dashboard.settings['worksheet'])

        def btn_configure_click(self, **event_args):
          dialogs.show_form('configure_form', width=900, height=900)
          self.refresh_data_bindings()

        def btn_submit_click(self, **event_args):
          # If the user hasn't filled out the override and comment fields
          # and if they haven't selected anything, return
          if not all([
            self.text_box_override.text,
            self.text_box_comment.text,
            self.worksheet.get_selected_marks()[0]
          ]):
            return

          selected_record = self.worksheet.get_selected_marks()[0]

          app_tables.overrides.add_row(
            id_value = selected_record[self.dashboard.settings['id_field']],
            id_field = self.dashboard.settings['id_field'],
            override_field = self.dashboard.settings['override_field'],
            override_value = self.text_box_override.text,
            who = selected_record[self.dashboard.settings['username']],
            comment = self.text_box_comment.text,
            on = datetime.now()
          )
          self.repeating_panel_1.items = app_tables.overrides.search()

          # Refresh the Anvil datasource
          self.dashboard.get_datasource('overrides (postgres)').refresh()

          anvil.Notification('Override saved!').show()

          # Reset our text boxes
          self.text_box_comment.text = ''
          self.text_box_override.text = None

Now everytime an override is added the datasource will update!

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/finished_product.gif

.. admonition:: Looking for more to do?

  * If you'd like to keep working on this extension, here are some new features you could implement:

    * Handle multiple overrides for the same state
    * Show the timestamp and user who made the comment in the Tableau tooltip
    * Hide the "Submit" button in the ``Homepage`` form until a user selects a state on the dashboard

  * If you're looking for something new, consider working through the next tutorial, :doc:`/tutorials/salesforce/index`, which shows how Salesforce can be integrated into an extension using |ProductName|.

.. admonition:: Download the resources used in this tutorial!

    .. button-link:: https://anvil.works/build#clone:IHOJEUVWBQMU3LMD=WRAOCEA3FLDDZU2VNI7RVTNE
        :color: primary
        :shadow:

        :octicon:`link;1em;` Click here to clone a finished version of this extension

    .. button-link:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/Value+Override+Starter+Workbook.twbx
        :color: primary
        :shadow:

        :octicon:`graph;1em;` Click here to download the Tableau workbook
