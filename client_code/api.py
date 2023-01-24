import anvil
import anvil.js

from .model.proxies import _Tableau

__version__ = "0.2"


def get_environment():
    """Returns a dictionary of useful information about the environment the extension is currently running in.

    See a description of each here: https://tableau.github.io/extensions-api/docs/interfaces/environment.html#apiversion

    Returns
    -------

    :obj:`dict`
      A dictionary containing items such as the Tableau API version, Tableau version, operating system,
      and others.

    Example
    -------
    >>> from tableau_extensions import api
    >>> print(api.get_environment())
    {'apiVersion': '1.9.0', 'context': 'desktop', 'country': None, 'language': 'en', 'locale': 'en-us', 'mode': 'authoring', 'operatingSystem': 'win', 'tableauVersion': '2022.1.8'}
    """
    from anvil import tableau

    env = tableau.extensions.environment
    attrs = [
        "apiVersion",
        "context",
        "country",
        "language",
        "locale",
        "mode",
        "operatingSystem",
        "tableauVersion",
    ]
    return {attr: env.get(attr) for attr in attrs}


def get_dashboard():
    """Gets the instance of Tableau Dashboard that represents the current connection. This is
    the recommended entry point to the Tableau Extensions API.

    Returns
    -------

    :obj:`~client_code.model.proxies.Dashboard`
        The Dashboard instance associated with the current session.
        It is recommended that this is the only way you 'get' the current dashboard,
        since it is an attribute of Session, which deals with a bunch of house-keeping.

    Example
    -------
    >>> from tableau_extensions import api
    >>> mydashboard = api.get_dashboard()
    """
    return _Tableau.session().dashboard
