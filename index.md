# Talon-AI-Tools Documentation

:::{toctree}
:maxdepth: 1
docs/index.md
:::

.. include:: ../README.md
:parser: myst*parser.sphinx*

.. include:: ./README.md
:parser: myst*parser.sphinx*

.. include:: README.md
:parser: myst*parser.sphinx*

# README

'''{include} ../README.md
:relative-images:
'''

:::{include} README.md
:end-before: "# Collaborators"
:::

:::{include} ../README.md
:::

:::{include} ./README.md
:::

:::{include} README.md
:::
