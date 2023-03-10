# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../"))


def setup(app):
    app.add_css_file("custom.css")


# -- Project information -----------------------------------------------------

PRODUCT_NAME = "Anvil X"
WRAPPER_NAME = "trexjacket"

project = WRAPPER_NAME
copyright = "2023, Baker Tilly Inc"
author = "Baker Tilly Inc."


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_design",
]
autodoc_mock_imports = [
    "anvil.server",
    "anvil.js",
    "anvil.code_completion_hints",
    "anvil.tableau",
    "client_code._trex.Viewer._anvil_designer",
    "client_code.dialogs._standard_alert._anvil_designer",
    "client_code.dialogs._standard_confirm._anvil_designer",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# add_module_names = False

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# Show methods / classes / functions by their order in the source code
# instead of aphabetically
autodoc_member_order = "bysource"

# Create an index
html_use_index = True

rst_prolog = f"""
.. |WrapperName| replace:: {WRAPPER_NAME}

.. |ProductName| replace:: {PRODUCT_NAME}
"""
