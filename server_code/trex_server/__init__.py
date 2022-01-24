from hashlib import md5
from uuid import uuid4

import anvil.server
from anvil.tables import app_tables

from ..trex.model import Trex
from .file import DEFAULT_LOGO, get_file


def trex_from_row(row):
    obj = Trex()
    obj.uid = uuid4().hex
    obj.capability = anvil.server.Capability(["tableau.trex", obj.uid])
    obj.capability.set_update_handler(obj._handle_cache_update)
    if row["details"] is not None:
        obj.__dict__.update(row["details"])
    obj.logo = row["logo"]
    obj.file = row["file"]
    return obj


@anvil.server.callable("tableau.private.get_trex")
def get(app_id):
    row = app_tables.trex.get(app_id=app_id) or app_tables.trex.add_row(
        app_id=app_id, logo=DEFAULT_LOGO
    )
    return trex_from_row(row)


def _update_required(trex, row):
    details_match = trex.details == row["details"]
    logos_match = md5(trex.logo.get_bytes()) == md5(row["logo"].get_bytes())
    return not all((details_match, logos_match))


@anvil.server.callable("tableau.private.save_trex")
def save(trex):
    _, uid = anvil.server.unwrap_capability(
        trex.capability, ["tableau.trex", anvil.server.Capability.ANY]
    )
    try:
        assert uid == trex.uid
    except AssertionError:
        raise PermissionError("You do not have permission to update this object.")

    row = app_tables.trex.get()
    if row["file"] is None or _update_required(trex, row):
        file = get_file(trex.details, trex.logo)
        row.update(details=trex.details, logo=trex.logo, file=file)
        trex.capability.send_update({"file": file})
