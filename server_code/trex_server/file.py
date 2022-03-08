import base64
import io
import xml.etree.ElementTree as et

import anvil.server
import anvil.media
from PIL import Image

required_author_fields = ["name", "email", "website"]
optional_author_fields = ["organization"]

encoded_logo = b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAALEwAACxMBAJqcGAAAAlhJREFUOI2Nkt9vy1EYh5/3bbsvRSySCZbIxI+ZCKsN2TKtSFyIrV2WuRCJuBiJWxfuxCVXbvwFgiEtposgLFJElnbU1SxIZIIRJDKTrdu+53Uhra4mce7Oe57Pcz7JOULFisViwZ+29LAzOSjQYDgz1ZcCvWuXV11MJpN+OS/lm6179teqH0yDqxPTCyKSA8DcDsyOmOprnCaeP7459pdgy969i0LTC3IO/RQMyoHcQN+3cnljW3dNIFC47qDaK3g7BwdTkwBaBELT4ZPOUVWgKl4ZBnjxJPUlMDnTDrp0pmr6RHFeEjjcUUXPDGeSEwDN0Xg8sivxMhJNjGzbHd8PkM3eHRfkrBM5NkcQaY2vUnTlrDIA0NoaX+KLXFFlowr14tvVpqb2MICzmQcKqxvbumv+NAhZGCCIPwEw6QWXKYRL/VUXO0+rAUJiPwAk5MIlgVfwPjjHLCL1APmHN94ZdqeYN+NW/mn6I4BvwQYchcLnwFhJMDiYmlRxAzjpKWZkYkUCcZ2I61wi37tLbYyjiN0fHk5Oz3nGSLSzBbNHCF35R7f6K1/hN9PRhek11FrymfQQQKB4+Gl05P2qNRtmETlXW7e+b2z01dfycGNbfFMAbqNyKp9Jp4rzOT8RYFs0njJkc2iqsCObvTsOsDWWqA5C1uFy+Uz/oXJeKwVT4h0RmPUXhi79vuC0Ku6yOffTK3g9lfxfDQAisY516sg5kfOCiJk7HoLt2cf9b/9LANAc7dznm98PagG1fUOZ9IP5uMB8Q4CPoyNvausapkTt3rNMuvdf3C/o6+czhtdwmwAAAABJRU5ErkJggg=="
msg = base64.b64decode(encoded_logo)
buf = io.BytesIO(msg)
buf.seek(0)
DEFAULT_LOGO = anvil.BlobMedia("image/png", content=buf.read(), name="default_logo.png")

byteImgIO = io.BytesIO()
with anvil.media.TempFile(DEFAULT_LOGO) as temp_file:
    byteImg = Image.open(temp_file)
byteImg.save(byteImgIO, "PNG")
byteImgIO.seek(0)
byteImg = byteImgIO.read()
dataBytesIO = io.BytesIO(byteImg)
icon = base64.b64encode(dataBytesIO.read())  # bytes string
DEFAULT_ICON = icon.decode("utf8")  # serializable string


def get_url_for_branch(branch=None):
    "Returns the URL for the specified branch."
    url = anvil.server.get_app_origin("published")
    return url


def get_id_from_url(url):
    if url[:5] != "https":
        raise ValueError(
            "Your extension must be https, and the URL must begin with https://."
        )

    db_ext_id = url.split("://")[1]
    db_ext_id = db_ext_id.split("/")[0]
    db_ext_id = db_ext_id.split(".")[::-1]
    db_ext_id[0] = db_ext_id[0][:6]
    db_ext_id = ".".join(db_ext_id)
    return db_ext_id


def prettify_etree(root):
    # From StackExchange: Get URL and put it here
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    indent(root)


def check_fields(*args):
    for arg in args:
        if type(arg) is list:
            [check_fields(v) for v in arg]
        if type(arg) is dict:
            [check_fields(v) for v in arg.values()]

        elif type(arg) is str:
            if len(arg) > 1000:
                raise ValueError("Can't use strings longer than 1000 characters.")

        else:
            check_fields(str(arg))


def _build_trex_etree(
    source,
    source_id,
    author,
    name,
    description,
    default_locale="en_US",
    version="0.1.0",
    icon=None,
    branch=None,
    full_permission=False,
):
    check_fields(author, name, description)

    missing_fields = [field for field in required_author_fields if field not in author]
    if len(missing_fields) > 0:
        raise ValueError(f"Missing field(s) in author: {missing_fields}")

    extra_fields = [
        field
        for field in author
        if field not in required_author_fields + optional_author_fields
    ]
    if len(extra_fields) > 0:
        raise ValueError("Unrecognized field(s) in author: {missing_fields}")

    defaults = {
        "default-locale": default_locale,
        "name": {"resource-id": name},
        "description": description,
        "author": author,
        "min-api-version": "1.0",
    }

    manifest_details = {
        "manifest-version": "0.1",
        "xmlns": "http://www.tableau.com/xml/extension_manifest",
    }
    dashboard_extension_details = {"id": source_id, "extension-version": version}

    # Generate element tree
    root = et.Element("manifest", manifest_details)
    db = et.Element("dashboard-extension", dashboard_extension_details)
    root.append(db)

    for key in defaults:
        val = defaults[key]
        if isinstance(val, str):
            node = et.Element(key)
            node.text = val
            db.append(node)
        elif isinstance(val, dict):
            et.SubElement(db, key, val)
        else:
            raise TypeError(f"Didn't expect val to be of type {type(val)}")

    # Add source location node
    source_node = et.Element("source-location")
    url_node = et.Element("url")
    url_node.text = source
    source_node.append(url_node)
    db.append(source_node)

    icon_node = et.Element("icon")
    icon_node.text = icon
    db.append(icon_node)

    # Conditionally add full permission node
    if full_permission:
        permission_node = et.Element("permission")
        permission_node.text = "full data"
        permissions_node = et.Element("permissions")
        permissions_node.append(permission_node)
        db.append(permissions_node)

    prettify_etree(root)
    return et.ElementTree(element=root)


def get_file(details, logo, locale="en_US", version="0.1.0", branch=None):
    """Creates a trex file for the extension app"""
    # check for required fields
    # CHECK BRANCH AND GET URL
    url = get_url_for_branch(branch)
    url_id = get_id_from_url(url)
    icon = DEFAULT_ICON

    # Get the author details as required by _build_trex_etree
    author = {
        "name": details["author_name"],
        "email": details["author_email"],
        "website": details["author_website"],
    }
    if details["author_org"]:
        author["organization"] = details["author_org"]

    if logo:
        # From https://stackoverflow.com/questions/31077366/pil-cannot-identify-image-file-for-io-bytesio-object
        # Response by sdikby
        byteImgIO = io.BytesIO()
        with anvil.media.TempFile(logo) as temp_file:
            byteImg = Image.open(temp_file)
        byteImg.save(byteImgIO, "PNG")
        byteImgIO.seek(0)
        byteImg = byteImgIO.read()
        dataBytesIO = io.BytesIO(byteImg)
        icon = base64.b64encode(dataBytesIO.read())  # bytes string
        icon = icon.decode("utf8")  # serializable string

    # Build the XML file
    etree = _build_trex_etree(
        url,
        url_id,
        author,
        details["name"],
        details["description"],
        default_locale=locale,
        version=version,
        icon=icon,
        full_permission=details["full_permission"],
    )

    # Convert to media and return
    bs = io.BytesIO()
    etree.write(bs, encoding="utf8", method="xml")
    bs.seek(0)
    trex_media = anvil.BlobMedia(
        "application/xml", content=bs.read(), name="my_trex.trex"
    )
    return trex_media
