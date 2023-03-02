Supported objects and events
-----------------------------

``trexwrapper`` enables the user to listen and respond to **events** on **objects** in a Tableau dashboard using **event handlers**.

* **Objects** are the pieces of the Tableau dashboard that a user interacts with. The following objects are supported:

    * Dashboard (:py:class:`~client_code.model.proxies.Dashboard`)
    * Worksheet (:py:class:`~client_code.model.proxies.Worksheet`)
    * Filter (:py:class:`~client_code.model.proxies.Filter`)
    * Parameter (:py:class:`~client_code.model.proxies.Parameter`)
    * Datasource (:py:class:`~client_code.model.proxies.Datasource`)

* **Events** are triggered when a user interacts with *objects* on the dashboard. The following events are supported:

    * Changing a filter (:py:class:`~client_code.model.proxies.FilterChangedEvent`)
    * Changing a parameter (:py:class:`~client_code.model.proxies.ParameterChangedEvent`)
    * Selecting marks (:py:class:`~client_code.model.proxies.MarksSelectedEvent`)

* **Event handlers** are the functions and methods that respond to the events above. These functions can do anything you want them to! For example:

.. code-block:: python
    :linenos:

    from trexjacket.api import get_dashboard
    dashboard = get_dashboard().register_event_handler('selection_changed', notify_selection)

    def notify_selection(event):
        print(f'Someone selected these marks: {event.get_selected_marks()}')
