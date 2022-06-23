import anvil
import anvil.js

from .model.proxies import Tableau


def get_session():
    """Get a Tableau Session object.

    Returns
    -------
    :obj:`~client_code.model.proxies.Tableau`
    """
    return Tableau.session()


def get_dashboard():
    """Gets the instance of Tableau Dashboard that represents the current connection.

    Returns
    -------

    :obj:`~client_code.model.proxies.Dashboard`
        The Dashboard instance associated with the current session.
        It is recommended that this is the only way you 'get' the current dashboard,
        since it is an attribute of Session, which deals with a bunch of house-keeping.

    Examples
    --------
    >>> from tableau_extension.api import get_dashboard
    >>> get_dashboard().name
    'mydashboard'

    >>> get_dashboard().get_filters
    [abc, def, ghi]
    """
    return Tableau.session().dashboard
