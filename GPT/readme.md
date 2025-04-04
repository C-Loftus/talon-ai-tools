# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See [the list of available models](lists/model.talon-list) that can be used to specify which model to use directly in the voice command (e.g., "four o mini explain this").

- See the [examples file](../.docs/usage-examples/examples.md) for gifs that show how to use the commands.

- View the [docs](http://localhost:4321/talon-ai-tools/) for more detailed usage and help

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

To add additional prompts, copy the [Talon list for custom prompts](lists/customPrompt.talon-list.example) to anywhere in your user directory and add your desired prompts. These prompts will automatically be added into the `<user.modelPrompt>` capture.

If you wish to change any configuration settings, copy the [example configuration file](../talon-ai-settings.talon.example) into your user directory and modify settings that you want to change.

### Model-Specific Configuration

For advanced configuration of specific models, you can create a `models.json` file in the root directory of this repository. Copy `models.json.example` to `models.json` as a starting point, and then customize it to your needs.

The `models.json` file allows you to define per-model settings including:

- Model aliases (via `model_id`)
- Model-specific system prompts
- API options (like temperature, top_p, etc.)
- LLM CLI options (used when `user.model_endpoint` is set to "llm")

The configuration is automatically reloaded when the file changes, so you don't need to restart Talon after making changes.

### Global Settings

| Setting                  | Default                                                                                                                                                                                                                                                            | Notes                                                                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| user.model_default       | `"gpt-4o-mini"`                                                                                                                                                                                                                                                    | The default model to use when no specific model is specified in the command. You can also specify a model directly in the voice command, e.g., "four o mini explain this" |
| user.model_endpoint      | `"https://api.openai.com/v1/chat/completions"`                                                                                                                                                                                                                     | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)                                                                                         |
| user.model_shell_default | `"bash"`                                                                                                                                                                                                                                                           | The default shell for `model shell` commands                                                                                                                              |
| user.model_system_prompt | `"You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested."` | The meta-prompt for how to respond to all prompts (can be overridden per-model in models.json)                                                                            |
