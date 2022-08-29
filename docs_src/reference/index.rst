API Reference
=======

Overview
-----

The classes and other objects here are divided into 3 major sections:

1. Entry point
2. Tableau objects
3. Change event classes

Entry point
-----

These are things you use to first connect to your dashboard.

.. automodule:: client_code.api
   :members:

Tableau objects
-----

These are the things you can see on the dashboard.

.. automodule:: client_code.model.proxies
   :members: Dashboard, Parameter, Filter, Datasource, Worksheet
   :show-inheritance:

Change event classes
-----

These are classes you will interact with after registering an event handler.

.. automodule:: client_code.model.proxies
   :members: MarksSelectedEvent, FilterChangedEvent, ParameterChangedEvent

Technical Reference
-----

Things you probably don't need to know about.

.. automodule:: client_code.model.proxies
   :members: TableauProxy