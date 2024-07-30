# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See the [examples file](../.docs/usage-examples/examples.md) for gifs that show how to use the commands.

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

## Providing Contextual User Context

In case you want to provide additional context to the LLM, there is a hook that you can override in your own python code and anything that is returned will be sent with every request. This is useful for example if you would like to run a shell command and send its output along. Here is an example file that you can use as a template:

```
from talon import Context, Module, actions

mod = Module()

ctx = Context()


@ctx.action_class("user")
class UserActions:
    def contextual_user_context():
        """This is an override function that can be used to add additional context to the prompt"""
        result = actions.user.talon_get_active_context()
        return [
            f"The following describes the currently focused application:\n\n{result}"
        ]
```
