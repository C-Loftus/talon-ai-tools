# VSCode Copilot

This directory contains some very experimental commands for interacting with Copilot.

## Inline chat / refactoring / code generation

There are some commands to interact with the inline chat, leveraging Cursorless targets:

| Command                               | Description                                                                                                  | Example                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| `"pilot change <target>"`             | selects target and opens inline chat to enable typing instructions for how Copilot should change the target. | `"pilot change funk air"`                                     |
| `"pilot change <target> to <phrase>"` | tells Copilot to apply the instructions in `<phrase>` to the target.                                         | `"pilot change funk air to remove arguments"`.                |
| `"pilot test <target>"`               | Asks copilot to generate a test for the target.                                                              | `"pilot test funk air"`                                       |
| `"pilot doc <target>"`                | Asks copilot to generate documentation for the target.                                                       | `"pilot doc funk air"`                                        |
| `"pilot fix <target>"`                | Tells copilot to fix the target.                                                                             | `"pilot fix funk air"`                                        |
| `"pilot fix <target> to <phrase>"`    | Tells copilot to fix the target using the instructions in `<phrase>`.                                        | `"pilot fix funk air to remove warnings"`                     |
| `"pilot make <phrase>"`               | Tells copilot to generate code using the instructions in `<phrase>`, at the current cursor position.         | `"pilot make a function that returns the sum of two numbers"` |

## Chat sidebar

There are some commands to interact with the chat sidebar:

| Command                                 | Description                                                                                    | Example                                                                  |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `"pilot chat"`                          | opens chat to enable typing                                                                    |                                                                          |
| `"pilot chat hello world"`              | opens chat, types "hello world" and hits enter                                                 |                                                                          |
| `"pilot bring <ordinal>"`               | inserts nth code block in most recent chat response into your editor at cursor position        | `"pilot bring first"`, `"pilot bring last"`, `"pilot bring second last"` |
| `"pilot copy <ordinal>"`                | copies nth code block in most recent chat response                                             | `"pilot copy first"`                                                     |
| `"pilot bring <ordinal> <destination>"` | inserts nth code block in most recent chat response into your editor at Cursorless destination | `"pilot bring first after state air"`, `"pilot bring first to line air"` |
| `"pilot bring first to funk"`           | replaces function containing your cursor with first code block in most recent chat response    |                                                                          |
