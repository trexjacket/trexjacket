import anvil
import anvil.js
from _session import TableauSession
from .events import register_event_handler

from ._trex.Viewer import Viewer

session = TableauSession()


def show_trex():
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
