Chapter 3: Responding to events
================================

Now that our Extension is connected to our dashboard, let's use an event handler to respond to when user selects a mark on the dashboard.

.. dropdown::
    :open:

    .. image:: https://extension-documentation.s3.amazonaws.com/tutorials/chat/eventhandler.gif

.. tip::

  An event handler is a method that is called whenever an event occurs, for example, when the user makes a selection on the dashboard. You can create an event handler using the ``register_event_handler`` method from |ProductName|.

In the code pane for ``Form1``, create and register the event handler using the following code (changes highlighted).

.. code-block:: python
  :linenos:
  :emphasize-lines: 11,13-15

  from ._anvil_designer import Form1Template
  from anvil import *
  from anvil import tableau

  from trexjacket.api import get_dashboard
  dashboard = get_dashboard()

  class Form1(Form1Template):
    def __init__(self, **properties):
      self.init_components(**properties)
      dashboard.register_event_handler('selection_changed', self.selection_changed_event_handler)

    def selection_changed_event_handler(self, event):
      user_selection = event.worksheet.get_selected_marks()
      print(f"Got a selected record: {user_selection}, with length: ({len(user_selection)})")

``register_event_handler`` takes 2 arguments:

1. The kind of event we want to respond to (``'selection_changed'`` in this case)

2. The method that will execute when the event occurs (``self.selection_changed_event_handler``)

Now that we've created and registered our event handler, let's test it out! Reload your extension in Tableau and click on a state. Return to the Anvil IDE and see the output in the "Tableau Output 1" pane (see gif).
