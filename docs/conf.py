# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Talon-AI-Tools"
copyright = "2024 Colton Loftus"
author = "Colton Loftus, Joshua Aretsy, Pokey Rule, and others from the Talon Community"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Enables support for Markdown
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    "myst_parser",
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
    "substitution",
]

# -- Options for TalonDoc ----------------------------------------------------

talon_package = {
    "path": ".",
    "name": "user",
    "exclude": ["conf.py", "video_thumbnail.jpg", "usage-examples"],
    "trigger": "ready",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"


myst_substitutions = {"author": author}
