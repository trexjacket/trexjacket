Supported objects and events
-------------

This library enables the user to listen for *events* on *objects* in a Tableau dashboard.

* **Objects** are the pieces of the Tableau dashboard that a user interacts with. The following objects are supported:

    * Dashboard (:py:class:`~client_code.model.proxies.Dashboard`)
    * Worksheet (:py:class:`~client_code.model.proxies.Worksheet`)
    * Filter (:py:class:`~client_code.model.proxies.Filter`)
    * Parameter (:py:class:`~client_code.model.proxies.Parameter`)

* **Events** are triggered when a user interacts with *objects* on the dashboard. The following events are supported:

    * Changing a filter (:py:class:`~client_code.model.proxies.FilterChangedEvent`)
    * Changing a parameter (:py:class:`~client_code.model.proxies.ParameterChangedEvent`)
    * Selecting marks (:py:class:`~client_code.model.proxies.MarksSelectedEvent`)


?? Any event can be listened for by any object, as the image below demonstrates. Check if this is true


.. image:: eventsonobjects.PNG