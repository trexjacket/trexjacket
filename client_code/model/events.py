from anvil.js import report_exceptions


class _EventType:
    pass


FILTER_CHANGED = type("FilterChanged", (_EventType,), {})
PARAMETER_CHANGED = type("ParameterChanged", (_EventType,), {})
SELECTION_CHANGED = type("SelectionChanged", (_EventType,), {})

_event_types = {
    "filter_changed": FILTER_CHANGED,
    "parameter_changed": PARAMETER_CHANGED,
    "selection_changed": SELECTION_CHANGED,
}


def register_event_handler(event_type, handler, targets, mapper):
    """A function to register an event handler"""
    if isinstance(event_type, str):
        event_type = _event_types[event_type]
    handler = report_exceptions(handler)
    tableau_event = mapper.tableau_event(event_type)

    def wrapper(event):
        wrapped_event = mapper.proxy(event)
        handler(wrapped_event)

    for target in targets:
        target._proxy.addEventListener(tableau_event, wrapper)