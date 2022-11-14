import anvil
import anvil.js

from .model.proxies import _Tableau

__version__ = "0.0.1"


def get_dashboard():
    """Gets the instance of Tableau Dashboard that represents the current connection. This is
    the recommended entry point to the Tableau Extensions API.

    Returns
    -------

    :obj:`~client_code.model.proxies.Dashboard`
        The Dashboard instance associated with the current session.
        It is recommended that this is the only way you 'get' the current dashboard,
        since it is an attribute of Session, which deals with a bunch of house-keeping.
    """
    return _Tableau.session().dashboard
