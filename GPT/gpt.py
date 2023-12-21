import requests
import json, os
from talon import Module, actions, clip, app, settings
from typing import Literal

# TODO: Make it only available to run one request at a time

mod = Module() 
# Stores all our prompts that don't require arguments 
# (ie those that just take in the clipboard text)
mod.list("promptNoArgument", desc="GPT Prompts Without Arguments")
mod.setting(
    "llm_provider",
    type=Literal["OPENAI", "LOCAL_LLAMA"],
    default="OPENAI",
)


# Defaults to Andreas's custom notifications if you have them installed
def notify(message: str):
    try:
        actions.user.notify(message)
    except:
        app.notify(message)

def gpt_query(prompt: str, content: str) -> str:

    notify("GPT Task Started")

    match PROVIDER := settings.get("user.llm_provider"):

        case "OPENAI":
            try:
                TOKEN = os.environ["OPENAI_API_KEY"]
            except:
                notify("GPT Failure: No API Key")   
                return ""
            
            url = 'https://api.openai.com/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {TOKEN}'
            }
            data = {
                'messages': [{'role': 'user', 'content': f"{prompt}:\n{content}"}],
                'max_tokens': 2024,
                'temperature': 0.6,
                'n': 1,
                'stop': None,
                'model': 'gpt-3.5-turbo'
            }
        
        case "LOCAL_LLAMA":
            url = "http://localhost:8080/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {
                        "role": "system",
                        "content": "You are an assistant helping an office worker to be more productive."
                    },
                    {
                        'role': 'user', 
                        'content': f"{prompt}:\n{content}"
                    }
                ],
            }
        case _:
            raise ValueError(f"Unknown LLM provider {PROVIDER}")
            
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:

        notify("GPT Task Completed")

        return response.json()['choices'][0]['message']['content'].strip()
    else:
        notify("GPT Failure: Check API Key or Prompt")
        print(response.content)
        return ""

def gpt_task(prompt: str, content: str) -> str:
    """Run a GPT task"""

    resp = gpt_query(prompt, content)

    if resp:
        clip.set_text(resp)

    return resp

@mod.action_class
class UserActions:

    def gpt_prompt_no_argument(prompt: str) -> str:
        """Run a GPT task"""

        content = actions.edit.selected_text()

        return gpt_task(prompt, content)

    def gpt_answer_question(inputText: str) -> str:
        """Answer an arbitrary question"""
        prompt = """
        Generate text that satisfies the question or request given in the prompt. 
        """

        return gpt_task(prompt, inputText)


