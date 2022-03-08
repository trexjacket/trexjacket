import anvil
import anvil.js

from model.events import register_event_handler
from .model.proxies import TableauSession

from ._trex.Viewer import Viewer

session = TableauSession.get_session()

def get_session():
  return TableauSession.get_session()

def show_trex():
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
