Chapter 5: Adding new comments
==============================

In the previous chapter we saved information about the user's selection. In this chapter we'll build the front end that allows users to create their comments.

Step 1: Getting comment info
----------------------------

Let's start by adding a text box and button component to our form.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/createcommentinput.gif

In the gif above, we add:

* A Button, called ``btn_save``, with its click event bound to the ``btn_save_click`` method

    * Note that we need to scroll down and click ">>" to create the ``btn_save_click`` method. Now, whenever a user clicks that button, ``btn_save_click`` is called.

* A TextBox, called ``tb_comment``

Let's open the ``btn_save_click`` method and add some code that shows what the user commented, along with the selection information we configured in the previous chapter. We can access the content of the text box using its ``text`` attribute: It will also be useful to know when a comment was made, so let's import the ``datetime`` module at the top of ``Form1``s code.

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    from ._anvil_designer import Form1Template
    from anvil import *
    from anvil import tableau

    from trexjacket.api import get_dashboard
    dashboard = get_dashboard()

    from datetime import datetime

    # rest of Form1 code omitted

and add some code to the ``btn_save_click`` method that was created:

.. code-block:: python

    def btn_save_click(self, **event_args):
        comment_info = {
            'user': self.logged_in_user,
            'comment': self.tb_comment.text,
            'id': self.state_name,
            'value': self.profit,
            'at': datetime.now()
        }
        Notification(str(comment_info)).show()
        self.tb_comment.text = ""

Reload your extension and add a comment to the text box, then click "Save comment". You should see a popup that contains ``comment_info``!

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/createcomment.gif

Step 2: Saving to a data table
------------------------------

Now we have a way to capture what the user has commented, but we need a way to save these comments when a user leaves the extension. We can use Anvil Data Tables for this!

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/createdb.gif

In Anvil, select the "Data" icon on the left hand side and then click "Add New Table". Create a table named ``comments`` with the following columns:

* user: ``Text``
* comment: ``Text``
* id: ``Text``
* value: ``Number``
* at: ``Date and Time``

Additionally, be sure to select the "Can search, edit, and delete" option under the Form permission.

.. warning::

    You'd never allow forms to search / edit/ and delete from a datatable in a production application, but for the sake of the tutorial we'll do that for now.

Now that we've created a datatable, let's modify ``btn_save_click`` to write to our datatable instead of just showing the comment information:

.. code-block:: python
    :emphasize-lines: 2-8

    def btn_save_click(self, **event_args):
        app_tables.comments.add_row(
            user=self.logged_in_user,
            comment=self.tb_comment.text,
            id=self.state_name,
            value=self.profit,
            at=datetime.now()
        )
        self.tb_comment.text = ""

At this point, selecting a state and adding a comment should start populating the ``comments`` datatable! In the next chapter we'll build the UI to show what comments have already been made.


.. dropdown:: Click to view the full code for ``Form1``

    .. code-block:: python
        :linenos:
        :emphasize-lines: 34-42

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
