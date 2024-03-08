# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Usage

| Command                                                       | Description                                                          | Example                                       |
| ------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------- |
| `model ask <text>`                                            | Ask a question to the model                                          | "model ask what is the meaning of life"       |
| `model <prompt>`                                              | Generate text from a prompt and paste it                             | "model summarize"                             |
| `model clip <prompt>`                                         | Generate text from a prompt and set it on the clipboard              | "model clip summarize"                        |
| `model help`                                                  | Show the help menu with all the prompts                              | "model help"                                  |
| `model please <text>`                                         | Say an arbitrary prompt and then apply it                            | "model please translate this to Japanese"     |
| `model <prompt> <cursorless_target> <cursorless_destination>` | Select with cursorless, apply a prompt, and paste to the destination | "model explain line this after block red air" |

## Help

- See [the list of prompts](./staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See the [examples file](./examples.md) for gifs that show how to use the commands.

## Setup

In order to use this repository with GPT 3.5, you need [an OpenAI API key](https://platform.openai.com/signup).

- Once you get the key, set the environment variable within a Python file anywhere in your Talon user directory.
- **Make sure you do not push the key to a public repo!**

```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

If you want to change any configuration settings copy the example configuration file from `GPT/gpt-talon.settings.example` to `GPT/gpt-talon.settings`, which is a .git ignored file and modify anything that you want to change.

| Setting                  | Default                                                                                                                                   | Notes                                                                              |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| user.openai_model        | "gpt-3.5-turbo"                                                                                                                           | The model to use for the queries. NOTE: To access gpt-4 you may need prior API use |
| user.model_temperature   | 0.6                                                                                                                                       | Higher temperatures will make the model more creative and less accurate            |
| user.model_endpoint      | https://api.openai.com/v1/chat/completions                                                                                                | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)  |
| user.model_system_prompt | "You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content." | The meta-prompt for how to respond to prompts                                      |
