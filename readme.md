# Talon-GPT

Use LLM tools alongside Talon. Helpful to automatically generate text or fix errors in dictation.

## Setup

In order to use this repository you need an openai API key. Once you get the key, set the environment variable within a Python file in your Talon user directory. **Make sure you do not push the key to a public repo!**

```python
import os
os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

## TODO

- Create prompts that take in arguments from voice commands.
- Make the the help menu less verbose.
- Support llamafiles or other ways to run models locally.
- Support openai vision model
