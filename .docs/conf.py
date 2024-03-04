# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

from sphinx.application import Sphinx

project = "TalonDoc"
copyright = "2022, Wen Kokke"
author = "Wen Kokke"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.append(os.path.abspath("../.."))

extensions = [
    # Enables support for Markdown
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    "myst_parser",
    # Enables support for tabs
    # https://sphinx-tabs.readthedocs.io/en/latest/#sphinx-tabs
    "sphinx_tabs.tabs",
    # Enable support for Talon
    "talondoc.sphinx",
]

# -- Options for MyST --------------------------------------------------------

myst_enable_extensions = [
    # Enables colon fence directives
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#syntax-colon-fence
    "colon_fence",
    # Enables definition lists
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#definition-lists
    "deflist",
]

# -- Options for Sphinx Tabs -------------------------------------------------

# Disable tab closing.
# https://sphinx-tabs.readthedocs.io/en/latest/#sphinx-configuration
sphinx_tabs_disable_tab_closing = True

# Disable default CSS stylesheet.
# Custom stylesheet is added under 'Options for HTML output'.
# # https://sphinx-tabs.readthedocs.io/en/latest/#sphinx-configuration
sphinx_tabs_disable_css_loading = True


# -- Options for TalonDoc ----------------------------------------------------

talon_package = {
    "name": "user",
    "path": "../knausj_talon",
    "exclude": [
        "conftest.py",
        "test/stubs/talon/__init__.py",
        "test/stubs/talon/grammar.py",
        "test/stubs/talon/experimental/textarea.py",
        "test/repo_root_init.py",
        "test/test_code_modified_function.py",
        "test/test_create_spoken_forms.py",
        "test/test_dictation.py",
        "test/test_formatters.py",
    ],
    "trigger": "ready",
}

# def talon_docstring_hook(sort: str, name: str) -> Optional[str]:
#     return None
#

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

def setup(app: Sphinx) -> None:
    # Add custom styles for Sphinx Tabs
    app.add_css_file("css/custom-tabs.css")
    # Add custom styles for fragmenting tables
    app.add_css_file("css/custom-fragtables.css")
    # Add custom script for fragmenting tables
    app.add_js_file("js/custom-fragtables.js")
