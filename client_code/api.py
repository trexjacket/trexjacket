import anvil
import anvil.js

from .model.proxies import Tableau


def get_session():
    """Get a Tableau Session object.

    Returns
    -------
    :obj:`~client_code.model.proxies.Tableau`
        The current Tableau session.
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
    Get the name of the dashboard as a string

    >>> from tableau_extension.api import get_dashboard
    >>> get_dashboard().name
    'Example Dashboard'

    Get a list of all the filters in the dashboard

    >>> from tableau_extension.api import get_dashboard
    >>> get_dashboard().filters
    [<tableau_extension.model.proxies.Filter object>, <tableau_extension.model.proxies.Filter object>]
    """
    return Tableau.session().dashboard
