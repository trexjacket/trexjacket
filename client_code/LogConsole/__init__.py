from .._logging import register_default_handlers
from ..model.proxies import Tableau
from ._anvil_designer import LogConsoleTemplate


class LogConsole(LogConsoleTemplate):
    def __init__(self, **properties):
        self.session = Tableau.session()
        register_default_handlers(self.session)
        self.init_components(**properties)

    def form_show(self, **event_args):
        self.session.logger.register_console(self.logging_console)

    def form_hide(self, **event_args):
        self.session.logger.remove_console(self.logging_console)

    def button_clear_click(self, **event_args):
        self.logging_console.text = ""
