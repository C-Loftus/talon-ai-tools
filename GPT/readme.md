# GPT and LLM Interaction

Query language models with voice commands

## Setup

In order to use this repository with GPT 3.5, you need an OpenAI API key. Once you get the key, set the environment variable within a Python file in your Talon user directory. **Make sure you do not push the key to a public repo!**

```python
import os
os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

## Local Models

You can use this repository with a [llamafile](https://github.com/Mozilla-Ocho/llamafile). Set the value `user.llm_provider = "LOCAL_LLAMA"` in `gpt-settings.talon` to change the default model.

These models are easy to install and run entirely offline. They can be downloaded from the [llamafile](https://github.com/Mozilla-Ocho/llamafile) repository and require no setup. All you need to do is simply run the following in a terminal to run the model as a server in the background. Then if you have the `user.llm_provider` set, it will handle all your queries locally with no other setup needed.

```sh
.\llava-v1.5-7b-q4-server.llamafile --nobrowser
```

Keep in mind that running a model in the background is resource intensive and it will be slow unless you have a GPU on your computer.

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## TODO

- Create prompts that take in arguments from voice commands.
- Make the the help menu less verbose.
- Support openai vision model
