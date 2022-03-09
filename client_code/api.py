import anvil
import anvil.js

from ._trex.Viewer import Viewer
from .model.proxies import Tableau


def get_session():
    return Tableau.session()


def show_trex():
    session = get_session()
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
