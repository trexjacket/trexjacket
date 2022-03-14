from ..model.proxies import Tableau
from ._anvil_designer import LogConsoleTemplate


class LogConsole(LogConsoleTemplate):
    def __init__(self, **properties):
        self.session = Tableau.session()
        dashboard = self.session.dashboard
        dashboard.register_event_handler("filter_changed", self._on_filter_change)
        dashboard.register_event_handler("parameter_changed", self._on_parameter_change)
        dashboard.register_event_handler("selection_changed", self._on_selection_change)
        self.init_components(**properties)

    def form_show(self, **event_args):
        self.session.logger.register_console(self.logging_console)

    def form_hide(self, **event_args):
        self.session.logger.remove_console(self.logging_console)

    def button_clear_click(self, **event_args):
        self.logging_console.text = ""

    def _on_filter_change(self, event):
        logger = self.session.logger
        logger.log("*" * 50)
        logger.log("Filter Change detected...")
        logger.log(f"** Field Name: {event.filter.field_name}")
        logger.log(f"** Values: {event.filter.applied_values}")
        logger.log("*" * 50)

    def _on_parameter_change(self, event):
        logger = self.session.logger
        logger.log("*" * 50)
        logger.log("Parameter Change detected...")
        logger.log(f"** Parameter name: {event.parameter.name}")
        logger.log(f"** Parameter value: {event.parameter.value}")
        logger.log("*" * 50)

    def _on_selection_change(self, event):
        logger = self.session.logger
        logger.log("*" * 50)
        logger.log("Selection Change detected...")
        logger.log(f"** Worksheet name: {event.worksheet.name}")
        logger.log(f"** Worksheet type: {event.worksheet.sheetType}")
        logger.log(f"** Records: {event.worksheet.selected_records}")
        for mark in event.worksheet.selected_marks:
            logger.log(f"** {mark}")
        logger.log("*" * 50)
