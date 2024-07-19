# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Usage

| Command                                                       | Description                                                          | Example                                       |
| ------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------- |
| `model <prompt>`                                              | Generate text from a prompt and paste it                             | "model summarize"                             |
| `model help`                                                  | Show the help menu with all the prompts                              | "model help"                                  |
| `model please <text>`                                         | Say an arbitrary prompt and then apply it                            | "model please translate this to Japanese"     |
| `model ask <text>`                                            | Ask a question to the model                                          | "model ask what is the meaning of life"       |
| `model <prompt> <cursorless_target> <cursorless_destination>` | Select with cursorless, apply a prompt, and paste to the destination | "model explain line this after block red air" |
| `model <prompt> below`                                        | Apply a prompt and then paste the result below the cursor            | "model format bullets below"                  |
| `model <prompt> clipped`                                      | Apply a prompt and return the result in the clipboard                | "model explain this clipped"                  |

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See the [examples file](../docs/usage-examples/examples.md) for gifs that show how to use the commands.

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

To add additional prompts, copy the [Talon list for custom prompts](lists/customPrompt.talon-list.example) to anywhere in your user directory and add your desired prompts. These prompts will automatically be added into the `<user.modelPrompt>` capture.

If you wish to change any configuration settings, copy the [example configuration file](../talon-ai-settings.talon.example) into your user directory and modify settings that you want to change.

| Setting                  | Default                                                                                                                                                                                                                                                            | Notes                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| user.openai_model        | `"gpt-4o-mini"`                                                                                                                                                                                                                                                    | The model to use for the queries. NOTE: To access certain models you may need prior API use |
| user.model_temperature   | `0.6`                                                                                                                                                                                                                                                              | Higher temperatures will make the model more creative and less accurate                     |
| user.model_endpoint      | `"https://api.openai.com/v1/chat/completions"`                                                                                                                                                                                                                     | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)           |
| user.model_shell_default | `"bash"`                                                                                                                                                                                                                                                           | The default shell for `model shell` commands                                                |
| user.model_system_prompt | `"You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested."` | The meta-prompt for how to respond to all prompts                                           |
