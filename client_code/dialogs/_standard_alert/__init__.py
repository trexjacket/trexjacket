import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil import *
from anvil import tableau
from anvil.tables import app_tables

from .._registration import dialog_form
from ._anvil_designer import _standard_alertTemplate


@dialog_form("_standard_alert")
class _standard_alert(_standard_alertTemplate):
    def __init__(self, text=None, buttons=None, **properties):
        buttons = buttons or {"Okay": True}
        self.label_text.text = text
        self.return_values = {}
        for label, return_val in buttons.items():
            button = Button(text=label)
            self.return_values[button] = return_val
            button.add_event_handler("click", self.button_clicked)
            self.flow_panel_1.add_component(button)

        self.init_components(**properties)

    def button_clicked(self, **event_args):
        sender = event_args["sender"]
        self.raise_event("x-close-alert", value=self.return_values[sender])
