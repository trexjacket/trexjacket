Chapter 6: Displaying comments
==============================

In the last chapter we saved the comments to a database. In this chapter we'll build the UI that shows what comments have already been made.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/createdatagrid.gif

Click the "Design" button on ``Form1`` in Anvil. Then, let's drag a Data Grid component on to the page and name it ``dg_comments``. Set the ``Name`` and ``Key`` property for each column to the following:

.. list-table:: Data Grid Details
    :header-rows: 1

    * - Name
      - Key

    * - Comment
      - comment

    * - By
      - user

    * - At
      - at

    * - State
      - id

    * - Profit Ratio
      - value


.. note::
    Data grids are special in that when you add one to your UI, a repeating panel is automatically created inside of it. In this case, the data grid we created will create a Repeating Panel component named ``repeating_panel_1``, which you will see in the code block below.

    Additionally, when we defined the "Key" for each column in the data grid, the repeating panel will use that key to access a value from whatever we pass in to the repeating panels ``items`` attribute. In our case we're setting ``items`` to rows from the ``comments`` table, and using the column names as its keys.

Now let's update our ``__init__`` method to populate the data grid with the rows from the ``comments`` table.

.. code-block:: python
    :emphasize-lines: 8

    # imports omitted

    class Form1(Form1Template):
        def __init__(self, **properties):
          self.state_name = None
          self.profit = None
          self.logged_in_user = None
          self.repeating_panel_1.items = app_tables.comments.search()
          self.init_components(**properties)
          dashboard.register_event_handler('selection_changed', self.selection_changed_event_handler)

        # selection_changed_event_handler and btn_save_click omitted

and our ``btn_save_click`` to update when a new comment is made:

.. code-block:: python
    :emphasize-lines: 12

    # Form1 code omitted

    def btn_save_click(self, **event_args):
        app_tables.comments.add_row(
          user=self.logged_in_user,
          comment=self.tb_comment.text,
          id=self.state_name,
          value=self.profit,
          at=datetime.now()
        )
        self.tb_comment.text = ""
        self.repeating_panel_1.items = app_tables.comments.search()


Reload your extension in your dashboard, add a comment, and watch the table update!

.. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/finaloutput.gif

.. admonition:: Congrats! You now have a fully functioning Tableau Extension, built with |ProductName|.

  Looking for more to do? Check out the Value Override tutorial next to learn about dashboard settings. Or, try to add some of the following functionality to your chat extension:

  * Hide the "save comment" button until a user selects a mark
  * Format the "At" column of the data grid using ``strftime``
  * Handle multiple selections instead of just saving the first one
  * .. button-link:: https://anvil.works/build#clone:H6KTXT5CIJWB5AEW=O4PMZVRIQ6VZEETDJCOAYYMQ
       :color: primary
       :shadow:

       Or click here to clone a more built out version of the chat extension you just built

.. dropdown:: Click to view the full code for ``Form1``

    .. code-block:: python
        :linenos:
        :emphasize-lines: 18, 44

        from ._anvil_designer import Form1Template
        from anvil import *
        import anvil.tables as tables
        import anvil.tables.query as q
        from anvil.tables import app_tables
        from anvil import tableau

        from trexjacket.api import get_dashboard
        dashboard = get_dashboard()

        from datetime import datetime

        class Form1(Form1Template):
          def __init__(self, **properties):
            self.state_name = None
            self.profit = None
            self.logged_in_user = None
            self.repeating_panel_1.items = app_tables.comments.search()
            self.init_components(**properties)
            dashboard.register_event_handler('selection_changed', self.selection_changed_event_handler)

          def selection_changed_event_handler(self, event):
            user_selection = event.worksheet.get_selected_marks()

            if len(user_selection) == 0:
                self.state_name = None
                self.profit = None
                self.logged_in_user = None
            else:
                record = user_selection[0]
                self.state_name = record['State']
                self.profit = record['AGG(Profit Ratio)']
                self.logged_in_user = record['logged_in_user']

          def btn_save_click(self, **event_args):
            app_tables.comments.add_row(
              user=self.logged_in_user,
              comment=self.tb_comment.text,
              id=self.state_name,
              value=self.profit,
              at=datetime.now()
            )
            self.tb_comment.text = ""
            self.repeating_panel_1.items = app_tables.comments.search()
