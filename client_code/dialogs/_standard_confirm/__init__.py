import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil import *
from anvil import tableau
from anvil.tables import app_tables

from .._registration import dialog_form
from ._anvil_designer import _standard_confirmTemplate


@dialog_form("_standard_confirm")
class _standard_confirm(_standard_confirmTemplate):
    def __init__(self, text=None, **properties):
        self.label_text.text = text
        self.init_components(**properties)

    def button_cancel_click(self, **event_args):
        self.raise_event("x-close-alert", value=False)

    def button_okay_click(self, **event_args):
        self.raise_event("x-close-alert", value=True)
