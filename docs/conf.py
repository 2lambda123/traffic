# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from __future__ import annotations

import os
import sys
from typing import Any

import traffic

sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "traffic"
copyright = "2022, Xavier Olive"
author = "Xavier Olive"

# The short X.Y version
version = traffic.__version__
# The full version, including alpha/beta/rc tags
release = traffic.__version__


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "jupyter_sphinx",
]

# To avoid installing all dependencies when building doc
# https://stackoverflow.com/a/15912502/8729698
# autodoc_mock_imports = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}
html_theme_options = {
    "style_external_links": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = "_static/logo_traffic.png"

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "_static/favicon/favicon.ico"


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "traffic", "traffic Documentation", [author], 1)]


# -- Extension configuration -------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/dev", None),
    "shapely": ("https://shapely.readthedocs.io/en/latest", None),
    "cartopy": ("https://scitools.org.uk/cartopy/docs/latest", None),
    "pyproj": ("https://pyproj4.github.io/pyproj/stable", None),
    "altair": ("https://altair-viz.github.io", None),
    "cartes": ("https://cartes-viz.github.io", None),
    "ipyleaflet": ("https://ipyleaflet.readthedocs.io/en/latest/", None),
}


def setup(app: Any) -> None:
    # <!-- Import Vega & Vega-Lite -->
    app.add_js_file("https://cdn.jsdelivr.net/npm/vega@5")
    app.add_js_file("https://cdn.jsdelivr.net/npm/vega-lite@4")
    app.add_js_file("https://cdn.jsdelivr.net/npm/vega-embed@6")

    # Specific stylesheet
    app.add_css_file("main_stylesheet.css")
