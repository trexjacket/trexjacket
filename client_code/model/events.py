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


def register_event_handler(event_type, handler, targets, session):
    """A function to register an event handler"""
    if not session.available:
        raise ValueError("No tableau session is available")

    if isinstance(event_type, str):
        try:
            event_type = _event_types[event_type]
        except KeyError:
            raise KeyError(
                f"Unrecognized event_type {event_type}. "
                f"Valid events: {list(_event_types.keys())}"
            )

    try:
        _ = len(targets)
    except TypeError:
        targets = (targets,)

    handler = report_exceptions(handler)
    tableau_event = session.event_type_mapper.tableau_event(event_type)

    def wrapper(event):
        wrapped_event = session.event_type_mapper.proxy(event)
        handler(wrapped_event)

    for target in targets:
        target._proxy.addEventListener(tableau_event, wrapper)
