class MultipleTablesException(Exception):
    """Raised when a datasource has multiple underlying tables but
    an id was not passed.
    """

    pass
