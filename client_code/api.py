import anvil
import anvil.js

from ._trex.Viewer import Viewer
from .model.proxies import Tableau
from ._logging import Logger
from ._anvil_extras.messaging import Publisher


def get_session(logger=None, publisher=None, timeout=2):
    """Get a Tableau Session object.

    Parameters
    ----------
    logger : Logger
        Logger object to use for logging.
    publisher : Publisher
        Publisher object to use for messaging.
    timeout : int
        Timeout in seconds for the session.

    Returns
    -------
    Tableau
    """
    logger = Logger() if logger is None else logger
    publisher = Publisher() if publisher is None else publisher
    return Tableau.session(logger=logger, publisher=publisher, timeout=timeout)


def show_trex():
    """Display the Trex details form in an alert"""
    session = get_session()
    anvil.alert(
        content=Viewer(session.publisher),
        buttons=None,
        large=True,
        title="Trex Details",
    )
