Getting Started
==================

.. card:: Purpose

    The Tableau Extension library simplifies the development of tableau extensions using Anvil. 

Using **only python**, you can:

.. dropdown:: Get summary data of selected marks

    todo

.. dropdown:: Run code on filter change

    todo

.. dropdown:: Update a database when a user clicks a mark

    todo

.. dropdown:: Show dynamic images 

    todo


Demo
-------

Let's build a Tableau Extension that shows the summary data of selected marks when a user clicks or selects part of the dashboard.

.. note:: This demo assumes the Anvil app has a single label called `label_1`.

.. code-block:: python
    :linenos:

    # client_code/MainForm/__init__.py
    from ._anvil_designer import MainFormTemplate
    from anvil import *
    from tableau_extension.api import get_session

    session = get_session()

    class MainForm(MainFormTemplate):
        def __init__(self, **properties):
            self.init_components(**properties)
            self.dashboard = session.dashboard
            self.dashboard.register_event_handler('selection_changed', self.show_selections)

        def show_selections(self, event):
            self.label_1.text = str(event.worksheet.selected_records)

A few things to point out:

* We first create a session object, you'll probably be interacting with this a lot.
* In order to bind the code we want to run to a particular event, we use the `register_event_handler` method.
* Once we bind the event using `register_event_handler`, we define the function that does whatever we want.


.. note:: The class of the `event` argument in `show_selections` will be different based on what value is passed to `register_event_handler`. In this case, `event` is an instance of :py:func:`client_code.model.proxies.MarksSelectedEvent` because 'selection_changed' was passed.

.. dropdown:: Tada!
    :open:

    .. image:: firstexample.gif


More notes
-------------

* Run arbitrary python code in response to events on a tableau dashboard:

    * FilterChanged: User changes a filter
    * MarkSelectionChanged: User clicks a mark
    * ParameterChanged: User changes a parameter

* Change tableau filters and parameters from python code
* Refresh tableau data sources
* Enable write back capabilities
* ...and anything else possible with Python!


.. important:: 
    
    This library enables the user to listen for *events* on *objects* in a Tableau dashboard or workbook using Python.

    * Events: This is something the user will trigger by clicking a part of the dashboard or modifying something.

        * Changing a filter (FilterChangedEvent)
        * Changing a parameter (ParameterChangedEvent)
        * Selecting marks (MarkSelectionChangedEvent)

    * Objects: These are the pieces of the tableau dashboard.

        * Dashboard
        * Worksheet
        * Filter
        * Parameter

    ?? Any event can be listened for by any object, as the image below demonstrates. Check if this is true


.. image:: eventsonobjects.PNG