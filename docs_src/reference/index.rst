API Reference
=============

This reference documentation is divided into 3 major sections:

.. card:: 1. Connecting to the dashboard

   How to initially connect to the Tableau dashboard

.. card:: 2. Tableau objects

   Classes that represent things you can see on the dashboard (filters, parameters, marks, etc.)

.. card:: 3. Change event classes

   Classes that represent change events on the dashboard (mark selection, filter change, parameter change, etc.)

Connecting to the dashboard
-----------------------------

``api.get_dashboard`` is the recommended way to connect to the Tableau Dashboard.

.. automodule:: client_code.api
   :members:

Tableau objects
-----------------

These are the things you can see on the dashboard (filters, parameters, worksheets, etc.).

.. automodule:: client_code.model.proxies
   :members: Dashboard, Parameter, Filter, Datasource, Worksheet, Settings
   :show-inheritance:

Change event classes
--------------------

You will encounter these classes when registering event handlers. For example, when registering the 'filter_changed' event:

.. code-block:: python

   # in some form code
   def __init__(self):
      # setup code omitted
      self.dashboard.register_event_handler('filter_changed', self.my_event_handler)

   def my_event_handler(self, event):
      filter = event.filter

``event`` in this case will be an instance of the :obj:`~client_code.model.proxies.FilterChangedEvent` class.

.. automodule:: client_code.model.proxies
   :members: MarksSelectedEvent, FilterChangedEvent, ParameterChangedEvent

Displaying Dialogues
--------------------

.. automodule:: client_code.dialogs
   :members:
   :show-inheritance:


Technical Reference
--------------------

.. automodule:: client_code.model.proxies
   :members: TableauProxy
