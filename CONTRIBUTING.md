# Contributing

Thank you for your interest in contributing to `talon-ai-tools`. We are happy to receive new contributions. If you have any questions about contributing, feel free to ask.

## Contributing Python

- For all PRs please describe the purpose of the PR and give an example of any non-trivial functionality.
- Do not use external Python dependencies with `pip install`
  - This pollutes the Talon Python interpreter and can have unintended side effects
- Prefix all actions exposed from a module with `gpt_` or another appropriate prefix to distinguish it in the global namespace
  - i.e. Write a function like `actions.user.gpt_query()` not `actions.user.query()`
- Do not expose any actions globally with talon action classes if they don't need to be called from `.talon` files
- Comment all functions with doctrings and type annotations for arguments
- Any code that is intended to be reused within the repo should be placed within the `lib/` folder

## Contributing Talonscript

- Talon commands should follow a grammar that is intuitive for users or mimics the grammar of existing tools like Cursorless
  - Prefix all commands with an appropriate prefix like `model` or `pilot` to make sure they aren't accidentally run
- Duplicate commands following a similar syntax should be condensed into captures or lists _only_ if it improves readability for users or significantly reduces duplicate code for maintainers
  - It is better to duplicate code to make a command explicit and readable rather than overly condense the command within a fancy talon capture.
  - The commands inside a `.talon` file, to the extent possible, should be intuitive for a new user to understand. Numerous talon lists chained together requires a user to introspect code and adds friction to discoverability.
  - It is best to use talon commands that are very expliciti, even if overly verbose, and let the user customize them if desired. Brevity risks confusion.
- Any command that requires a capture or list should include a brief inline comment above it showing an example of the command and a one line description of what it does
- If a list is needed, `.talon-list` files should be used instead of defining lists inside Python
  - This makes it easier to customize list items by overriding the `.talon-list` and not needing to fork the Python.
- Avoid any configuration pattern that requires a user to fork this repository
