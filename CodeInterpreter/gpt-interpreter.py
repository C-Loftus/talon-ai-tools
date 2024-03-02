import json

import requests
from talon import Module, actions

from ..GPT.lib.gpt_helpers import get_token, notify

mod = Module()


@mod.action_class
class InterpreterActions:
    def gpt_code_interpret(instruction: str):
        """Run the given code instruction through OpenAI code interpreter and return the result."""

        TOKEN = get_token()

        url = "https://api.openai.com/v1/assistants"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
            "OpenAI-Beta": "assistants=v1",
        }
        data = {
            "instructions": instruction,
            "tools": [{"type": "code_interpreter"}],
            "model": "gpt-4-turbo-preview",
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        match response.status_code:
            case 200:
                notify("GPT Task Completed")
                print(response.json())
            case _:
                notify("GPT Failure: Check API Key, Model, or Prompt")
                print(response.json())
