from .._logging import register_default_handlers
from ..model.events import FILTER_CHANGED, PARAMETER_CHANGED, SELECTION_CHANGED
from ..model.proxies import Tableau
from ._anvil_designer import LogConsoleTemplate


class LogConsole(LogConsoleTemplate):
    def __init__(self, **properties):
        self.session = Tableau.session()

        # Establish default behavior per component properties
        event_types = []
        if self.log_filter_changed:
            event_types.append(FILTER_CHANGED)
        if self.log_parameter_changed:
            event_types.append(PARAMETER_CHANGED)
        if self.log_selection_changed:
            event_types.append(SELECTION_CHANGED)

        print(
            f"Registering logger with event handlers: {event_types}. Printing to console: {self.log_to_console}"
        )
        register_default_handlers(self.session, event_types)
        self.session.logger.with_anvil_logging = self.log_to_console

        self.init_components(**properties)

    def form_show(self, **event_args):
        self.session.logger.register_console(self.logging_console)

    def form_hide(self, **event_args):
        self.session.logger.remove_console(self.logging_console)

    def button_clear_click(self, **event_args):
        self.logging_console.text = ""

    def _refresh_bindings(self, **event_args):
        self.refresh_data_bindings()
