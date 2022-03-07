class EventType:
    pass


FILTER_CHANGED = type("FilterChanged", (EventType,), {})
PARAMETER_CHANGED = type("ParameterChanged", (EventType,), {})
SELECTION_CHANGED = type("SelectionChanged", (EventType,), {})

event_types = {
    "filter_changed": FILTER_CHANGED,
    "parameter_changed": PARAMETER_CHANGED,
    "selection_changed": SELECTION_CHANGED,
}
