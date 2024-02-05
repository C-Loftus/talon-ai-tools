from talon import Module, actions, clip, app, settings, imgui
from typing import Callable, List, Literal
import webbrowser, tempfile, requests, os, json

mod = Module()
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.setting(
    "llm_provider",
    type=Literal["OPENAI", "LOCAL_LLAMA"],
    default="OPENAI",
)

mod.setting(
    "openai_model", type=Literal["gpt-3.5-turbo", "gpt-4"], default="gpt-3.5-turbo"
)


text_to_confirm = ""


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


def gpt_query(prompt: str, content: str, insert_response: Callable[[str], str]) -> str:
    notify("GPT Task Started")

    match PROVIDER := settings.get("user.llm_provider"):
        case "OPENAI":
            try:
                TOKEN = os.environ["OPENAI_API_KEY"]
            except:
                notify("GPT Failure: env var OPENAI_API_KEY is not set.")
                return ""

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}",
            }
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"language:\n{actions.code.language()}",
                    },
                    {"role": "user", "content": f"{prompt}:\n{content}"},
                ],
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "insert",
                            "description": "insert(str: string) - this inserts the string into the document. The document is in the language specified so if you aren't careful you will case syntax errors.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "str": {
                                        "type": "string",
                                        "description": "The text to insert",
                                    }
                                },
                                "required": ["str"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "notify",
                            "description": "notify(str: string) - this notifies the user using a popup notification",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "str": {
                                        "type": "string",
                                        "description": "The text to notify",
                                    }
                                },
                                "required": ["str"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "display",
                            "description": "display(str: string) - DEFAULT - this displays the response to the user. Use this for all informational text aside from notifications. Use this instead of returning content in the response.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "str": {
                                        "type": "string",
                                        "description": "The text to display",
                                    }
                                },
                                "required": ["str"],
                            },
                        },
                    }
                ],
                "max_tokens": 2024,
                "temperature": 0.6,
                "n": 1,
                "stop": None,
                "model": settings.get("user.openai_model"),
            }

        case "LOCAL_LLAMA":
            url = "http://localhost:8080/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an assistant helping an office worker to be more productive.",
                    },
                    {"role": "user", "content": f"{prompt}:\n{content}"},
                ],
            }
        case _:
            raise ValueError(f"Unknown LLM provider {PROVIDER}")

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        notify("GPT Task Completed")
        print(response.json())

        try:
            tool_calls = response.json()["choices"][0]["message"]["tool_calls"]
            while tool_calls:
                tool = tool_calls.pop()
                first_argument = tool['function']['arguments']
                try:
                    first_argument = json.loads(first_argument)['str']
                except Exception as e:
                    notify(f"Argument Jason was malformed: {e}")
                if tool['function']['name'] == 'insert':
                    print(tool['function']['arguments'])
                    insert_response(tool['function']['arguments'])
                elif tool['function']['name'] == 'display':
                    actions.user.display_response(first_argument)
                elif tool['function']['name'] == 'notify':
                    actions.user.notify_user(first_argument)
        except Exception as e:
            notify(f"No tool_calls found in response from LLM: {e}")

        try:
            content = response.json()["choices"][0]["message"]["content"].strip()
            insert_response(content)
        except Exception as e:
            notify(f"No content found in response from LLM: {e}")

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
        return gpt_query(prompt, text_to_process, actions.user.paste)

    def gpt_generate_shell(text_to_process: str) -> str:
        """Generate a shell command from a spoken instruction"""
        prompt = """
        Generate a unix shell command that will perform the given task.
        Only include the code and not any natural language comments or explanations. 
        Condense the code into a single line such that it can be ran in the terminal.
        """

        # TODO potentially sanitize this further heuristically?
        gpt_query(prompt, text_to_process, actions.user.add_to_confirmation_gui)

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

    def gpt_apply_prompt(prompt: str, text_to_process: str) -> str:
        """Apply an arbitrary prompt to arbitrary text"""
        return gpt_query(prompt, text_to_process, actions.user.paste)

    def gpt_apply_prompt_clip(prompt: str, text_to_process: str) -> str:
        """Apply an arbitrary prompt to arbitrary text"""
        return gpt_query(prompt, text_to_process, actions.clip.set_text)

    def gpt_apply_cursorless_prompt(prompt: str, text_to_process: str, cursorless_destination: any):
        """Apply a cursorless prompt"""
        def insert_to_destination(result: str):
            actions.user.cursorless_insert(cursorless_destination, result)
        return gpt_query(prompt, text_to_process, insert_to_destination)

    def gpt_help():
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "staticPrompt.talon-list")
        with open(file_path, "r") as f:
            lines = f.readlines()[2:]

        # Create a temporary HTML file and write the content to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            # Write the HTML header with CSS for dark mode, larger font size, text wrapping, and margins
            f.write(
                b""" 
            <html>
            <head>
                <style>
                    body { 
                        background-color: #282a36; 
                        color: #f8f8f2; 
                        font-family: Arial, sans-serif; 
                        font-size: 18px; 
                        margin: 100px; 
                    }
                    pre { 
                        white-space: pre-wrap; 
                        word-wrap: break-word; 
                    }
                </style>
            </head>
            <body>
            <pre>
            """
            )

            # Write each line of the file, replacing newlines with HTML line breaks
            for line in lines:
                f.write((line.replace("\n", "<br>\n")).encode())

            # Write the HTML footer
            f.write(
                b"""
            </pre>
            </body>
            </html>
            """
            )

            temp_filename = f.name

        # Open the temporary HTML file in the web browser
        # Open the temporary HTML file in the web browser
        webbrowser.open("file://" + os.path.abspath(temp_filename))

    def notify_user(response: str):
        """Send a notification to the desktop"""
        print(response)
        actions.app.notify(title="Talon AI Tools", body=response)

    def display_response(response: str):
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "staticPrompt.talon-list")
        with open(file_path, "r") as f:
            lines = f.readlines()[2:]

        # Create a temporary HTML file and write the content to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            # Write the HTML header with CSS for dark mode, larger font size, text wrapping, and margins
            f.write(
                b""" 
            <html>
            <head>
                <style>
                    body { 
                        background-color: #282a36; 
                        color: #f8f8f2;
                        font-family: Arial, sans-serif; 
                        font-size: 18px; 
                        margin: 100px; 
                    }
                    pre { 
                        white-space: pre-wrap; 
                        word-wrap: break-word; 
                    }
                </style>
            </head>
            <body>
            <pre>
            """
            )
            f.write(response.encode())

            # Write the HTML footer
            f.write(
                b"""
            </pre>
            </body>
            </html>
            """
            )

            temp_filename = f.name

        # Open the temporary HTML file in the web browser
        webbrowser.open("file://" + os.path.abspath(temp_filename))
