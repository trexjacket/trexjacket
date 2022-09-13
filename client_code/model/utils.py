import datetime
import random

import anvil.js

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def clean_record_key(key):
    """Clean the record keys from tableau"""
    return key.replace("(generated)", "").strip()


class loading_indicator:
    def __enter__(self):
        anvil.js.call_js("setLoading", True)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        anvil.js.call_js("setLoading", False)


def native_value_date_handler(native_value):
    """Parses native_values into Python types. Floats, ints, strings, and booleans
    are handled without processing. Dates in Javascript don't distinguish between
    dates and datetimes, and are JS proxies, so these are converted explicitly into
    datetime.datetime or datetime.date objects, as appropriate."""
    if not hasattr(native_value, "toISOString"):
        return native_value

    # We are dealing with a JS Date object.
    iso_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    datetime_obj = datetime.datetime.strptime(native_value.toISOString(), iso_format)

    if all(
        [
            getattr(datetime_obj, part) == 0
            for part in ("microsecond", "second", "minute", "hour")
        ]
    ):
        return datetime_obj.date()
    else:
        return datetime_obj


def unique_id(length=8):
    return "".join([random.choice(ALPHABET) for _ in range(length)])
