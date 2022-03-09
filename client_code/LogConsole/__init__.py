from ._anvil_designer import LogConsoleTemplate
from ..model.proxies import Tableau


class LogConsole(LogConsoleTemplate):
    def __init__(self, **properties):
        self.logger = Tableau.session().logger
        self.init_components(**properties)

    def form_show(self, **event_args):
        self.logger.register_console(self.logging_console)

    def form_hide(self, **event_args):
        self.logger.remove_console(self.logging_console)

    def button_clear_click(self, **event_args):
        self.logging_console.text = ""
