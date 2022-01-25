import anvil
from anvil.js import report_exceptions

from ._trex.Viewer import Viewer
from .model import event_types, proxies


class event_handler:
    """A decorator class to register an event handling function

    NOTE - This does not work for registering methods
    """

    def __init__(self, event_type, targets):
        self.event_type = event_types[event_type]
        self.targets = targets

    def __call__(self, handler):
        handler = report_exceptions(handler)

        def wrapper(event):
            wrapped_event = proxies[event._type](event)
            handler(wrapped_event)

        for target in self.targets:
            target._proxy.addEventListener(self.event_type, wrapper)


def register_event_handler(handler, event_type, targets):
    """A function to register an event handler

    This will work for both ordinary functions and methods
    """
    handler = report_exceptions(handler)
    event_type = event_types[event_type]

    def wrapper(event):
        wrapped_event = proxies[event._type](event)
        handler(wrapped_event)

    for target in targets:
        target._proxy.addEventListener(event_type, wrapper)


def show_trex(publisher=None):
    anvil.alert(
        content=Viewer(publisher), buttons=None, large=True, title="Trex Details"
    )


def tableau_available():
    try:
        from anvil.js.window import tableau
        _ = tableau.extensions.dashboardContent.dashboard
        return True
    except AttributeError:
        return False
