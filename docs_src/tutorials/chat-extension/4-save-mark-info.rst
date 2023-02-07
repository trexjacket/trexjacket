Chapter 4: Getting comment details
==================================

In Chapter 4 we used ``get_selected_marks`` to get the user's selection from the Tableau Dashboard. In this chapter, we'll save the key fields we need to allow users to make a comment.

We want to get the name of the state and the profit from the dashboard, which are both contained in ``user_selection``. Let's add some code to our form that saves this information to form attributes:

.. code-block:: python
    :linenos:
    :emphasize-lines: 10-12, 19-30

    from ._anvil_designer import Form1Template
    from anvil import *
    from anvil import tableau

    from tableau_extension.api import get_dashboard
    dashboard = get_dashboard()

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

        msg = f"User: {self.logged_in_user}\nState: {self.state_name}\nProfit Ratio: {self.profit}"
        Notification(msg).show()

Once you've added this code in the code pane of ``Form1``, reload the extension inside Tableau and click on a few states. You should see the selection appearing as a popup in your extension!


.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/markselected.gif

In the next chapter we'll add the functionality for a user to add their comment.
