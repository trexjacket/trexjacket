import anvil
from anvil.js import report_exceptions

from . import model
from ._trex.Viewer import Viewer

_event_types = {
    "filter_changed": None,
    "selection_changed": None,
    "parameter_changed": None,
}
_proxies = {}
_tableau = None
dashboard = model.Dashboard()


def tableau_available():
    return _tableau is not None


def set_tableau():
    global _tableau, _event_types, _proxies
    from anvil.js.window import tableau

    _tableau = tableau

    _tableau.extensions.initializeAsync()
    _event_types = {
        "filter_changed": _tableau.TableauEventType.FilterChanged,
        "selection_changed": _tableau.TableauEventType.MarkSelectionChanged,
        "parameter_changed": _tableau.TableauEventType.ParameterChanged,
    }

    _proxies = {
        _tableau.TableauEventType.FilterChanged: model.FilterChangedEvent,
        _tableau.TableauEventType.MarkSelectionChanged: model.MarksSelectedEvent,
        _tableau.TableauEventType.ParameterChanged: model.ParameterChangedEvent,
    }
    dashboard.proxy = _tableau.extensions.dashboardContent.dashboard


set_tableau()


class event_handler:
    """A decorator class to register an event handling function

    NOTE - This does not work for registering methods
    """

    def __init__(self, event_type, targets):
        self.event_type = _event_types[event_type]
        self.targets = targets

    def __call__(self, handler):
        handler = report_exceptions(handler)

        def wrapper(event):
            wrapped_event = _proxies[event._type](event)
            handler(wrapped_event)

        for target in self.targets:
            target._proxy.addEventListener(self.event_type, wrapper)


def register_event_handler(handler, event_type, targets):
    """A function to register an event handler

    This will work for both ordinary functions and methods
    """
    handler = report_exceptions(handler)
    event_type = _event_types[event_type]

    def wrapper(event):
        wrapped_event = _proxies[event._type](event)
        handler(wrapped_event)

    for target in targets:
        target._proxy.addEventListener(event_type, wrapper)


def show_trex(publisher=None):
    anvil.alert(
        content=Viewer(publisher), buttons=None, large=True, title="Trex Details"
    )
