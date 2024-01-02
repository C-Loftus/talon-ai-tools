import requests
import json, os
from talon import Module, actions, clip, app, settings
from typing import Literal

mod = Module() 
# Stores all our prompts that don't require arguments 
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.setting(
    "llm_provider",
    type=Literal["OPENAI", "LOCAL_LLAMA"],
    default="OPENAI",
)

mod.setting("openai_model", type=Literal[
    "gpt-3.5-turbo", "gpt-4"
], default="gpt-3.5-turbo")


# Defaults to Andreas's custom notifications if you have them installed
def notify(message: str):
    try:
        actions.user.notify(message)
    except:
        app.notify(message)
    # Log in case notifications are disabled
    print(message)

def gpt_query(prompt: str, content: str) -> str:

    notify("GPT Task Started")

    match PROVIDER := settings.get("user.llm_provider"):

        case "OPENAI":
            try:
                TOKEN = os.environ["OPENAI_API_KEY"]
            except:
                notify("GPT Failure: env var OPENAI_API_KEY is not set.")   
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
                'model': settings.get("user.openai_model"),
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
        notify("GPT Failure: Check API Key, Model, or Prompt")


@mod.action_class
class UserActions:

    def gpt_answer_question(text_to_process: str) -> str:
        """Answer an arbitrary question"""
        prompt = """
        Generate text that satisfies the question or request given in the input. 
        """
        return gpt_query(prompt, text_to_process)

    def gpt_apply_prompt(prompt:str , text_to_process: str) -> str:
        """Apply an arbitrary prompt to arbitrary text""" 
        return gpt_query(prompt, text_to_process)

