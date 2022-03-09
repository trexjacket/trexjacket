import anvil
import anvil.js

from ._anvil_extras.messaging import Publisher
from ._logging import Logger
from ._trex.Viewer import Viewer
from .model.proxies import Tableau


def get_session(logger=None, publisher=None, timeout=2):
    logger = Logger() if logger is None else logger
    publisher = Publisher() if publisher is None else publisher
    return Tableau.session(logger=logger, publisher=publisher, timeout=timeout)


def show_trex():
    session = get_session()
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
