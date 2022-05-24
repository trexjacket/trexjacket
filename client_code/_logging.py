from time import gmtime, strftime, time

import anvil

from .model import events


def _timestamp(seconds):
    """Text representation of a unix timestamp"""
    return strftime("%Y-%m-%d %H:%M:%S", gmtime(seconds))


def _log_to_console(console, msg):
    if console.text:
        console.text += f"\n{msg}"
    else:
        console.text = msg


class _LoggingErrorHandler:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, err):
        self.logger.log("*** ERROR ***")
        self.logger.log(err)
        raise err


class Logger:
    def __init__(self, with_anvil_logging=True, prefix=">>>", history=10):
        self._messages = []
        self.with_anvil_logging = with_anvil_logging
        self.history = history
        self._consoles = []
        self.prefix = "" if prefix is None else prefix

    def register_console(self, component, show_history=True):
        if getattr(component, "text", None) is None:
            raise ValueError(
                f"{type(component)} has no text attribute and "
                "cannot be used as a console"
            )
        if show_history and len(self._messages) > 0:
            component.text = f"{self.prefix} Logger has unshown messages..."
            for msg in self._messages:
                component.text += f"\n{msg}"
            component.text += (
                f"\n{self.prefix} Flushed all unshown messages "
                f"(of max. {self.history} kept in logger history)."
            )
        msg = f"{self.prefix} Listening for logging messages..."
        _log_to_console(component, msg)
        self._consoles.append(component)

    def remove_console(self, component):
        self._consoles = [c for c in self._consoles if c != component]

    def log(self, message, with_anvil_logging=True):
        if with_anvil_logging or self.with_anvil_logging:
            print(f"{_timestamp(time())} GMT: {message}")
        msg = f"{self.prefix} {message}"
        self._messages.append(msg)
        if len(self._messages) > self.history:
            self._messages.pop(0)
        for console in self._consoles:
            _log_to_console(console, msg)

    def warn(self, message, with_anvil_logging=True):
        self.log(f"WARNING: {message}", with_anvil_logging)
        anvil.Notification(message=message, title="Warning", style="warning").show()


_all_event_types = events.event_types.values()


def register_default_handlers(session, event_types=_all_event_types):
    """Register simple logging handlers for the given event types

    Parameters
    ----------
    session : Tableau instance
    event_types : list or str
        List of event types to register handlers for. If None, all event types
        are registered.
    """
    if isinstance(event_types, str):
        event_types = [event_types]
    event_types = [
        events.event_types[e] if isinstance(e, str) else e for e in event_types
    ]
    logger = session.logger

    def _on_filter_change(event):
        logger.log("*" * 50)
        logger.log("Filter Change detected...")
        logger.log(f"** Field Name: {event.filter.field_name}")
        logger.log(f"** Values: {event.filter.applied_values}")
        logger.log("*" * 50)

    def _on_parameter_change(event):
        logger.log("*" * 50)
        logger.log("Parameter Change detected...")
        logger.log(f"** Parameter name: {event.parameter.name}")
        logger.log(f"** Parameter value: {event.parameter.value}")
        logger.log("*" * 50)

    def _on_selection_change(event):
        logger.log("*" * 50)
        logger.log("Selection Change detected...")
        logger.log(f"** Worksheet name: {event.worksheet.name}")
        logger.log(f"** Worksheet type: {event.worksheet.sheetType}")
        logger.log(f"** Records: {event.worksheet.selected_records}")
        for mark in event.worksheet.selected_marks:
            logger.log(f"** {mark}")
        logger.log("*" * 50)

    dashboard = session.dashboard
    if events.FILTER_CHANGED in event_types:
        dashboard.register_event_handler("filter_changed", _on_filter_change)
    if events.PARAMETER_CHANGED in event_types:
        dashboard.register_event_handler("parameter_changed", _on_parameter_change)
    if events.SELECTION_CHANGED in event_types:
        dashboard.register_event_handler("selection_changed", _on_selection_change)
