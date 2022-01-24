import anvil
import anvil.server

from ._anvil_designer import _TrexTemplate
class _Trex(_TrexTemplate):
    def __init__(self, **properties):
        self.item = anvil.server.call("tableau.private.get_trex", anvil.app.id)
        self.init_components(**properties)

    def button_save_click(self, **event_args):
        self.item.save()
        self.raise_event("x-close-alert")

    def button_cancel_click(self, **event_args):
        self.raise_event("x-close-alert")