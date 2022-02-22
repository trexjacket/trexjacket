class EventType:
    pass


FILTER_CHANGED = type("FilterChanged", (EventType,), {})
PARAMETER_CHANGED = type("ParameterChanged", (EventType,), {})
SELECTION_CHANGED = type("SelectionChanged", (EventType,), {})
