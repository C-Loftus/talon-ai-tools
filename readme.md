# Talon-AI-Tools

**Control large language models and AI tools through voice commands using the [Talon Voice](https://talon.wiki) dictation engine.**

This functionality is especially helpful for users who:

- want to quickly edit text and fix dictation errors
- code by voice using tools like [Cursorless](https://www.cursorless.org/)
- have health issues affecting their hands and want to reduce keyboard use
- want to speed up their workflow and use AI commands across the entire desktop

**Prompts and extends the following tools:**

- Github Copilot
- OpenAI API (GPT-3.5/GPT-4) for text generation and processing
  - Any OpenAI compatible model endpoint can be used (Azure, local llamafiles, etc)
- OpenAI API for image generation and vision

## Help and Setup:

1. Download or `git clone` this repo into your Talon user directory.
1. [Obtain an OpenAI API key](https://platform.openai.com/signup).

1. Create a Python file anywhere in your Talon user directory.
1. Set the key environment variable within the Python file

> [!CAUTION]
> Make sure you do not push the key to a public repo!

```python
# Example of setting the environment variable
import os

os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

> [!NOTE]  
> You can also use this repo without an OpenAI API key by using an offline model and [customizing the endpoint url](./GPT/readme.md#configuration) to be another model, or a local LLM.

### Quickstart Video

[![Talon-AI-Tools Quickstart](docs/video_thumbnail.jpg)](https://www.youtube.com/watch?v=FctiTs6D2tM "Talon-AI-Tools Quickstart")
