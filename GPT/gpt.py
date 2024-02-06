import re
from talon import Module, actions, clip, app, settings, imgui, registry
from typing import Literal
import requests, os, json
from .lib import HTMLbuilder
from concurrent.futures import ThreadPoolExecutor

mod = Module() 
mod.tag("gpt_beta")
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


text_to_confirm=""
@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()
    gui.text(text_to_confirm)

    gui.spacer()
    if gui.button("Paste model output"):
        actions.user.paste_model_confirmation_gui()
    
    gui.spacer()
    if gui.button("Copy model output"):
        actions.user.copy_model_confirmation_gui()

    gui.spacer()
    if gui.button("Deny model output"):
        actions.user.close_model_confirmation_gui()

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
        print(response.json())


@mod.action_class
class UserActions:

    def gpt_answer_question(text_to_process: str) -> str:
        """Answer an arbitrary question"""
        prompt = """
        Generate text that satisfies the question or request given in the input. 
        """
        return gpt_query(prompt, text_to_process)
    
    def gpt_generate_shell(text_to_process: str) -> str:
        """Generate a shell command from a spoken instruction"""
        prompt = """
        Generate a unix shell command that will perform the given task.
        Only include the code and not any natural language comments or explanations. 
        Condense the code into a single line such that it can be ran in the terminal.
        """

        # TODO potentially sanitize this further heuristically?
        result = gpt_query(prompt, text_to_process)
        return result
    
    def add_to_confirmation_gui(model_output: str):
        """Add text to the confirmation gui"""
        global text_to_confirm
        text_to_confirm = model_output
        confirmation_gui.show()
    
    def close_model_confirmation_gui():
        """Close the model output without pasting it"""
        global text_to_confirm
        text_to_confirm = ""
        confirmation_gui.hide()

    def copy_model_confirmation_gui():
        """Copy the model output to the clipboard"""
        global text_to_confirm
        clip.set_text(text_to_confirm)
        text_to_confirm = ""
        confirmation_gui.hide()

    def paste_model_confirmation_gui():
        """Paste the model output"""
        actions.user.paste(text_to_confirm)
        confirmation_gui.hide()
       
    def gpt_apply_prompt(prompt:str , text_to_process: str) -> str:
        """Apply an arbitrary prompt to arbitrary text""" 
        return gpt_query(prompt, text_to_process)

    def gpt_help():
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'staticPrompt.talon-list')
        with open(file_path, 'r') as f:
            lines = f.readlines()[2:]

        builder = HTMLbuilder.Builder()
        builder.h1("Talon GPT Prompt List")
        for line in lines:
            if "##" in line:
                builder.h2(line)
            else:
                builder.p(line)

        builder.render() 
    

    def gpt_find_talon_commands(command_description:str):
        """Search for relevant talon commands"""
        command_list = ""
        for ctx in registry.active_contexts():
            items = ctx.commands.items()
            for _, command in items:
                raw_command = remove_wrapper(str(command))
                delimited = f"{raw_command}\n"
                command_list += delimited

        prompt = f"""
        The following is a list of commands for a program that controls the user's desktop.
        I am a user and I want to find {command_description}.
        If there is no command return the exact word "None".
        """

        def split_into_chunks(text: str, chunk_size: int):
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        command_chunks = split_into_chunks(command_list, 1400 - len(prompt))

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(gpt_query, [prompt]*len(command_chunks), command_chunks))

        builder = HTMLbuilder.Builder()
        builder.h1("Talon GPT Command Response")
        for result in results:
            if result != "None":
                builder.p(result)
        builder.render()


def remove_wrapper(text: str):
    regex = r'[^"]+"([^"]+)"'
    match = re.search(regex, text)
    return match.group(1)
