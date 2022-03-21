from time import gmtime, strftime, time

import anvil
import anvil.server


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
        anvil.set_default_error_handling(_LoggingErrorHandler(self))

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
