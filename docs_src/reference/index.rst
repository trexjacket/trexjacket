API Reference
=======

Overview
-----

This reference documentation is divided into 3 major sections:

1. Connecting to the dashboard
2. Tableau objects
3. Change event classes

Connecting to the dashboard
-----

``api.get_dashboard`` is the recommended way to connect to the Tableau Dashboard.

.. automodule:: client_code.api
   :members:

Tableau objects
-----

These are the things you can see on the dashboard (filters, parameters, worksheets, etc.).

.. automodule:: client_code.model.proxies
   :members: Dashboard, Parameter, Filter, Datasource, Worksheet
   :show-inheritance:

Change event classes
-----

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

Technical Reference
-----

Things you probably don't need to know about.

.. automodule:: client_code.model.proxies
   :members: TableauProxy