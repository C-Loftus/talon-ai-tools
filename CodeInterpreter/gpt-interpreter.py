from talon import Module, actions
import requests
import json
from ..GPT.lib.gpt_helpers import get_token, notify 

mod = Module()

# https://medium.com/@darthfv0id/using-gpt-4-code-interpreter-api-to-analyze-csv-files-b2e36712b52c

@mod.action_class
class InterpreterActions:
    def gpt_code_interpret(instruction: str):
        """Run the given code instruction through OpenAI code interpreter and return the result."""

        TOKEN = get_token()

        url = "https://api.openai.com/v1/assistants"
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {TOKEN}",
            'OpenAI-Beta': 'assistants=v1'
        }
        data = {
                "instructions": instruction,
                "tools": [
                    { "type": "code_interpreter" }
                ],
                "model": "gpt-4-turbo-preview"
            }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        match response.status_code:
            case 200:
                notify("GPT Task Completed")
                print(response.json())
            case _:
                notify("GPT Failure: Check API Key, Model, or Prompt")
                print(response.json())


            # {'id': 'asst_l6bZo7Uy7ozJoT6p8dOAWnju', 'object': 'assistant', 'created_at': 1709401396, 'name': None, 'description': None, 'model': 'gpt-4-turbo-preview', 'instructions': 'generate plot of apple stock returns', 'tools': [{'type': 'code_interpreter'}], 'metadata': {}, 'file_ids': []}