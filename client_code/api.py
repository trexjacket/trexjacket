import anvil
import anvil.js
from _session import Session
from anvil.js import report_exceptions

from ._trex.Viewer import Viewer
from .events import event_types

session = Session()


class event_handler:
    """A decorator class to register an event handling function

    NOTE - This does not work for registering methods
    """

    def __init__(self, event_type, targets):
        if isinstance(event_type, str):
            event_type = event_types[event_type]
        self.event_type = event_type
        self.targets = targets

    def __call__(self, handler):
        handler = report_exceptions(handler)

        def wrapper(event):
            wrapped_event = session.event_type_mapper.proxy(event)
            handler(wrapped_event)

        tableau_event = session.event_type_mapper.tableau_event(self.event_type)
        for target in self.targets:
            target._proxy.addEventListener(tableau_event, wrapper)


def register_event_handler(event_type, handler, targets):
    """A function to register an event handler

    This will work for both ordinary functions and methods
    """
    if isinstance(event_type, str):
        event_type = event_types[event_type]
    handler = report_exceptions(handler)
    tableau_event = session.event_type_mapper.tableau_event(event_type)

    def wrapper(event):
        wrapped_event = session.event_type_mapper.proxy(event)
        handler(wrapped_event)

    for target in targets:
        target._proxy.addEventListener(tableau_event, wrapper)


def show_trex():
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
