import anvil
import anvil.js
from _session import TableauSession

from ._trex.Viewer import Viewer

session = TableauSession()


def show_trex():
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
