# TalonDoc

:::{toctree}
:maxdepth: 1

knausj_talon/index
:::

## Loading a Talon package

TalonDoc can analyse a Talon package or user directory. To load all Talon and
Python files in `example/knausj_talon` we add the following to `conf.py`:

```python
talon_package = {
  'path': '../knausj_talon',
  'name': 'user',
  'exclude': ['conftest.py', 'test/**'],
  'trigger': 'ready'
}
```

The `talon_package` value is required and describes the Talon package that
is being documented. It should be a dictionary with the key `path` whose
value is the path to the root directory of the Talon package. The path may be
relative to the `conf.py` file. The dictionary may optionally contain any of
the following keys:

`name`
: The name of the Talon package.
This is used to resolve `self.*` references.
Defaults to `user`.

`include`
: A list of glob patterns.
All `.talon` and `.py` files in the package directory are included by
default, but any file matched by an include pattern will be included _even
if_ it matches any of the patterns in `exclude`.

`exclude`
: A list of glob patterns.
Any file matched by an exclude pattern will be excluded _unless_ it matches
any of the patterns in `include`.

`trigger`
: A list of Talon events.
These events will be triggered after the entire package has been loaded.
Useful for making sure that "launch" and "ready" callbacks fire.

If the `talon_package` value is a string, and not a dictionary, it is
interpreted as the value of the `path` field.

If you wish to document multiple Talon packages, you can use `talon_packages`
whose value must be a list or tuple of package descriptions as described above.

:::{warning}
Sphinx can work with either reStructuredText or Markdown, but in order to work with Markdown you need to add the following to your `conf.py`:

```python
extensions = [
    # Enables support for Markdown
    # https://www.sphinx-doc.org/en/master/usage/markdown.html
    "myst_parser",

    # Other extensions
    # ...
]
```

Furthermore, in order to use the colon fence syntax (`:::`) used throughout this guide, you need to enable the `colon_fence` extension, by adding the following to your `conf.py`:

```python
myst_enable_extensions = [
    # Enables colon fence directives
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#syntax-colon-fence
    "colon_fence",

    # Other extensions
    # ...
]
```

For more information, see [the Sphinx documentation](https://www.sphinx-doc.org/en/master/usage/markdown.html) and [the MyST documentation](https://myst-parser.readthedocs.io/en/latest/).
:::

## Commands

### Individual Commands

TalonDoc can generate documentation for an individual command using `talon:command` by entering any phrase which triggers the command. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:command:: hunt this
:always_include_script:

.. talon:command:: hunt this pace
:always_include_script:
::::::

::::::{code-tab} markdown Markdown
:::{talon:command} hunt this
:always_include_script:
:::

:::{talon:command} hunt this pace
:always_include_script:
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:command} hunt this
:always_include_script:
:::

:::{talon:command} hunt this pace
:always_include_script:
:::

TalonDoc will attempt to generate documentation for the command using the
following three options, in order:

1. Use the Talon docstrings in the command script. Talon docstrings are comments which start with `###`.
2. Use the Python docstrings from the actions used in the command script.
3. Include the command script.

The `talon:command` directive take the following options:

`:always_include_script:`
: If specified, the literal script is _always_ included in the command description.

`:context:` and `:contexts:`
: The contexts in which to search for the command. Contexts can be specified using Talon context names, e.g., `user.apps.discord.discord` or `user.apps.discord.discord.talon`, or by using file names relative to the package root, _e.g._, `apps/discord/discord.talon`. Multiple contexts can be specified, in which case they should be separated by commas. If neither `:context:` nor `:contexts:` is specified, all commands are searched.

If the command is ambiguous it is necessary to specify the context. For instance, the command 'decline call' matches multiple commands in different contexts. Therefore, the following code will raise an error:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:command:: answer call
.. talon:command:: decline call
::::::

::::::{code-tab} markdown Markdown
:::{talon:command} answer call
:::
:::{talon:command} decline call
:::
::::::
:::::::::

...and it generates the following bad documentation. It inserts the ambiguous command verbatim, and does not generate any other documentation for it:

:::{talon:command} answer call
:::
:::{talon:command} decline call
:::

To generate the correct documentation you must specify the context in which it is defined. For example, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:command:: answer call
.. talon:command:: decline call
:context: user.apps.discord.discord
::::::

::::::{code-tab} markdown Markdown
:::{talon:command} answer call
:::
:::{talon:command} decline call
:context: user.apps.discord.discord
:::
::::::
:::::::::

...will generate the following, much better looking documentation:

:::{talon:command} answer call
:::
:::{talon:command} decline call
:context: user.apps.discord.discord
:::

### Tables of commands

TalonDoc can generate documentation for groups of commands via `talon:command-table`, which generates a table with two columns---the rule and the description as those generated by `talon:command`.

For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:command-table::
:caption: A little custom hunting table.
:include: hunt this, hunt this pace

.. talon:command-table::
:caption: A bigger custom Discord table.
:context: user.apps.discord.discord
::::::

::::::{code-tab} markdown Markdown
:::{talon:command-table}
:caption: A little custom hunting table.
:include: hunt this, hunt this pace
:::

:::{talon:command-table}
:caption: A bigger custom Discord table.
:context: user.apps.discord.discord
:::
::::::
:::::::::

... generates the following two tables:

:::{talon:command-table}
:caption: A little custom hunting table.
:include: hunt this, hunt this pace
:::

:::{talon:command-table}
:caption: A bigger custom Discord table.
:context: user.apps.discord.discord
:::

The `talon:command-table` directive take any number of arguments, which can either be file paths relative to the package root, _e.g._, `apps/discord/discord.talon`, or module names, _e.g._, `user.apps.discord.discord.talon`. For the latter, the `.talon` suffix is optional. If no arguments are given, commands are included from the _entire package_. Furthermore, these directives take the following options:

`:always_include_script:`
: If specified, the literal script is _always_ included in the command description.

`:context:` and `:contexts:`
: The contexts in which to search for the commands. Contexts can be specified using Talon context names, e.g., `user.apps.discord.discord` or `user.apps.discord.discord.talon`, or by using file names relative to the package root, _e.g._, `apps/discord/discord.talon`. Multiple contexts can be specified, in which case they should be separated by commas. If neither `:context:` nor `:contexts:` is specified, all commands are searched.

`:caption:`
: A caption for the table.
Defaults to the module name, if given.

`:include:`
: A list of command phrases. If `:include:` is specified, all commands matching one of these phrases are included. Otherwise, all commands are included.

`:exclude:`
: A list of command phrases.
If `:exclude:` is specified, any commands matching one of these phrases are excluded.

## Actions

TalonDoc can generate documentation for actions using `talon:action`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:action:: user.find
.. talon:action:: user.insert_formatted
::::::

::::::{code-tab} markdown Markdown
:::{talon:action} user.find
:::

:::{talon:action} user.insert_formatted
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:action} user.find
:::

:::{talon:action} user.insert_formatted
:::

## Captures

TalonDoc can generate documentation for captures using `talon:capture`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:capture:: user.any_alphanumeric_key
::::::

::::::{code-tab} markdown Markdown
:::{talon:capture} user.any_alphanumeric_key
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:capture} user.any_alphanumeric_key
:::

## Lists

TalonDoc can generate documentation for lists using `talon:list`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:list:: user.letter
.. talon:list:: user.symbol_key
::::::

::::::{code-tab} markdown Markdown
:::{talon:list} user.letter
:::
:::{talon:list} user.symbol_key
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:list} user.letter
:::
:::{talon:list} user.symbol_key
:::

## Modes

TalonDoc can generate documentation for modes using `talon:mode`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:mode:: command
.. talon:mode:: dictation
::::::

::::::{code-tab} markdown Markdown
:::{talon:mode} command
:::
:::{talon:mode} dictation
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:mode} command
:::
:::{talon:mode} dictation
:::

## Settings

TalonDoc can generate documentation for settings using `talon:setting`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:setting:: key_hold
::::::

::::::{code-tab} markdown Markdown
:::{talon:setting} key_hold
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:setting} key_hold
:::
:::{talon:setting} dictate.punctuation
:::

Setting documentation is restricted to names and descriptions.

## Tags

TalonDoc can generate documentation for tags using `talon:tag`. For instance, the following code:

:::::::::{tabs}
::::::{code-tab} rst reStructuredText
.. talon:tag:: user.find_and_replace
::::::

::::::{code-tab} markdown Markdown
:::{talon:tag} user.find_and_replace
:::
::::::
:::::::::

...will generate the following bit of documentation:

:::{talon:tag} user.find_and_replace
:::
