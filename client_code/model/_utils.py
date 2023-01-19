import datetime
from itertools import groupby
from operator import itemgetter

import anvil.js


def cleanup_measures(records):
    """Cleans up a list of dicts. Returns a list of dicts"""
    cols = list(records[0].keys())
    if "Measure Names" not in cols:
        return records

    measure_names = set([el["Measure Names"] for el in records])

    # These are the only columns we care about
    non_measure_columns = [x for x in cols if x not in measure_names]

    # This is what the values should be unique by
    index_columns = [
        x for x in non_measure_columns if x not in ["Measure Names", "Measure Values"]
    ]

    build_recs = []
    field_getters = itemgetter(*index_columns)
    records.sort(key=field_getters)
    for key, values in groupby(records, key=field_getters):
        key = key if isinstance(key, tuple) else (key,)
        collapsed_row = dict(zip(index_columns, key))
        collapsed_row.update({v["Measure Names"]: v["Measure Values"] for v in values})
        build_recs.append(collapsed_row)

    return build_recs


def _clean_columns(cols):
    """
    cols: list of Column proxy objects

    Returns a dictionary of column types keyed on
    the column name
    """
    return {x.fieldName: x.dataType for x in cols}


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
