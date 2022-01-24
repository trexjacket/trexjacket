from ._anvil_designer import LogConsoleTemplate


class LogConsole(LogConsoleTemplate):
    def __init__(self, **properties):
        self._logger = None
        self.init_components(**properties)

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    def form_show(self, **event_args):
        self.logger.register_console(self.logging_console)

    def form_hide(self, **event_args):
        self.logger.remove_console(self.logging_console)

    def button_clear_click(self, **event_args):
        self.logging_console.text = ""
