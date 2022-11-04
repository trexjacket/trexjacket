import datetime as dt
import json

import anvil.server


def _make_simple(x):
    """Returns a Simple Object of variable x that can be passed to/from the Anvil Server/Client.
    Simple Objects can be floats, booleans, ints, strings, dictionaries, lists, dates, datetimes, or tuples.
    This recursively unpacts and lists, dictionaries, and tuples while maintaining those data types.
    It gets the row ID for any Anvil Row objects, and otherwise calls the __str__ method of any objects.

    Takes:
    ------
        x : any
            The object that will be made simple

    Returns:
        y : simple obj
            The object made to be only simple types.
    """
    if type(x) in [float, bool, int, str] or x is None:
        y = x
    elif type(x) is dt.date:
        y = f"ISODate({x.isoformat()})"
    elif type(x) is dt.datetime:
        y = f"ISODateTime({x.isoformat()})"
    elif hasattr(x, "get_id") or hasattr(x, "to_csv"):
        raise TypeError(
            "Can't pass Anvil Table objects to/from dialog forms. Consider passing them "
            "as a dictionary or pass their row ids (using 'get_id')"
        )
    elif isinstance(x, dict):
        y = {k: _make_simple(x[k]) for k in x}
    elif isinstance(x, list):
        y = [_make_simple(i) for i in x]
    elif isinstance(x, tuple):
        y = tuple([_make_simple(i) for i in x])
    else:
        if hasattr(x, "__serialize__"):
            y = json.dumps(x.__serialize__())
        else:
            y = json.dumps(x)

        print(
            f"Object is not simple but is of type: {type(x)}. It is being serialized to: `{y}`. "
            "If this is a custom class, you can specify the serialization behavior by defining a `__serialize__` method."
        )
    return y


def _jsonify(obj):
    sobj = _make_simple(obj)
    jsonified = json.dumps(sobj)
    return jsonified


def _dejsonify(text):
    if text == "":
        return ""
    elif text is None:
        return None
    else:
        value = json.loads(text)
        if isinstance(value, str) and value.startswith("ISODate("):
            value = dt.date.fromisoformat(value[8:-1])
        elif isinstance(value, str) and value.startswith("ISODateTime("):
            value = dt.datetime.fromisoformat(value[12:-1])
        return value
