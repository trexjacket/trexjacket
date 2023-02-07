Chapter 2: Capturing Overrides
==============================

In the last chapter we configured our settings, and in this chapter we'll start to use those settings to capture overrides for different values.

Add components to the Homepage
------------------------------

Let's add the following components to the ``Homepage`` form:

* A Button named ``btn_submit``, click event bound to ``btn_submit_click``
* A Text Box named ``text_box_override``
* A Text Box named ``text_box_comment``

Once you're done, the ``Homepage`` form should look like this:

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/home_page_ui_start.PNG

And now let's add the code:

.. code-block:: python
  :linenos:
  :emphasize-lines: 12-15, 21-36

  from ._anvil_designer import HomepageTemplate
  import anvil

  from tableau_extension.api import get_dashboard
  from tableau_extension import dialogs

  class Homepage(HomepageTemplate):
    def __init__(self, **properties):
      self.dashboard = get_dashboard()
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
      anvil.Notification('We should save this!').show()

      # Reset our text boxes
      self.text_box_comment.text = ''
      self.text_box_override.text = None

Right now, if you enter an override and a comment and click the Submit button, you should see a notification but nothing else!

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/dummy_override.gif

This works, but let's start persisting this data using Anvil data tables.

Configure the data table
------------------------

Let's create a data table named ``overrides`` with the following columns:

* ``id_field``: Text
* ``id_value``: Text
* ``override_field``: Text
* ``override_value``: Text
* ``on``: Date and Time
* ``who``: Text
* ``comment``: Text

Make sure to select "Can search, edit and delete" next to permissions. We'd never do this in a production application but will for the tutorial.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/allow_client_write.gif


Now let's add a data grid to the ``Homepage`` form with the following 4 column names and keys:

.. list-table::
    :header-rows: 1

    * - Name
      - Key

    * - ID Field
      - id_field

    * - ID Value
      - id_value

    * - Override Field
      - override_field

    * - Override Value
      - override_value

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/add_data_grid.gif

Now that we have our data table and UI set up, let's save the user's override and comment to our data table. Add the following code to the ``Homepage`` form:


.. code-block:: python
  :linenos:
  :emphasize-lines: 3-4, 12, 36-46

  from ._anvil_designer import HomepageTemplate
  import anvil
  from anvil.tables import app_tables
  from datetime import datetime

  from tableau_extension.api import get_dashboard
  from tableau_extension import dialogs

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
      anvil.Notification('Override saved!').show()

      # Reset our text boxes
      self.text_box_comment.text = ''
      self.text_box_override.text = None

Now reload your extension in Tableau and you should be able to add a comment and an override!

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/value-override/save_override.gif

In the next chapter we'll connect Tableau directly to our data table so we can add the overrides to the dashboard tooltip.
