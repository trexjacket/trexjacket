Supported objects and events
-------------

This library enables the user to listen and respond to *events* on *objects* in a Tableau dashboard using *event handlers*.

* **Objects** are the pieces of the Tableau dashboard that a user interacts with. The following objects are supported:

    * Dashboard (:py:class:`~client_code.model.proxies.Dashboard`)
    * Worksheet (:py:class:`~client_code.model.proxies.Worksheet`)
    * Filter (:py:class:`~client_code.model.proxies.Filter`)
    * Parameter (:py:class:`~client_code.model.proxies.Parameter`)

* **Events** are triggered when a user interacts with *objects* on the dashboard. The following events are supported:

    * Changing a filter (:py:class:`~client_code.model.proxies.FilterChangedEvent`)
    * Changing a parameter (:py:class:`~client_code.model.proxies.ParameterChangedEvent`)
    * Selecting marks (:py:class:`~client_code.model.proxies.MarksSelectedEvent`)

Dashboard and Worksheet objects currently support registering event handlers for all 3 types of events, while Parameter only supports event handlers on parameter changed events. Adding event handlers to filters is not supported.