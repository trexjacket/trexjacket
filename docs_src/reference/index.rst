API Reference
=======

This reference documentation is divided into 3 major sections:

1. Connecting to the dashboard

   - Documents how to initally connect to the Tableau dashboard

2. Tableau objects

   - Classes that represent things you can see on the dashboard (filters, parameters, marks, etc.)

3. Change event classes

   - Classes that represent change events on the dashboard (mark selection, filter change, parameter change, etc.)

4. Technical reference

   - Details of some under the hood functionality.

Connecting to the dashboard
-----

``api.get_dashboard`` is the recommended way to connect to the Tableau Dashboard.

.. automodule:: client_code.api
   :members:

Tableau objects
-----

These are the things you can see on the dashboard (filters, parameters, worksheets, etc.).

.. automodule:: client_code.model.proxies
   :members: Dashboard, Parameter, Filter, Datasource, Worksheet, Settings
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

Documentation for developers requiring a lower level of functionality.

.. automodule:: client_code.model.proxies
   :members: TableauProxy


.. autoclass:: client_code.model.proxies.Dashboard
   :members:
