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
import commonmark
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

here = os.path.abspath(os.path.dirname(__file__))
freshbooks_sdk = os.path.join(here, "..", "..", "freshbooks")


# -- Project information -----------------------------------------------------
with open(os.path.join(freshbooks_sdk, "VERSION")) as f:
    version = f.readlines()[0].strip()

project = "freshbooks-sdk"
copyright = "2022, Andrew McIntosh"
author = "Andrew McIntosh"

# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "autodoc2",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.githubpages",
    'sphinx.ext.napoleon',
    "enum_tools.autoenum",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

autodoc2_packages = [
    {
        "path": "../../freshbooks",
        "auto_mode": False
    }
]
"""
autodoc2_docstring_parser_regexes = [
    # this will render all docstrings as Markdown
    (r".*", "myst"),
]
autodoc2_docstrings = "all"
"""

# Allow markdown in docstrings


def docstring(app, what, name, obj, options, lines):
    md = '\n'.join(lines)
    ast = commonmark.Parser().parse(md)
    rst = commonmark.ReStructuredTextRenderer().render(ast)
    lines.clear()
    lines += rst.splitlines()


def setup(app):
    app.connect('autodoc-process-docstring', docstring)
