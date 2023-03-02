class _EventType:
    pass


FILTER_CHANGED = type("FilterChanged", (_EventType,), {})
PARAMETER_CHANGED = type("ParameterChanged", (_EventType,), {})
SELECTION_CHANGED = type("SelectionChanged", (_EventType,), {})

event_types = {
    "filter_changed": FILTER_CHANGED,
    "parameter_changed": PARAMETER_CHANGED,
    "selection_changed": SELECTION_CHANGED,
}
