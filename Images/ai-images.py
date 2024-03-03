import base64
import os
import webbrowser

import requests
from talon import Module, clip

from ..GPT.lib.gpt_helpers import get_token, notify

mod = Module()

mod.list("descriptionPrompt", desc="Prompts for describing images")
mod.list("generationPrompt", desc="Prompts for generating images")


def get_clipboard_image():
    try:
        clipped_image = clip.image()
        if not clipped_image:
            raise Exception("No image found in clipboard")

        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return base64_image
    except Exception as e:
        print(e)
        raise Exception("Invalid image in clipboard")


def upload_file():
    TOKEN = get_token()
    url = "https://api.openai.com/v1/files"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    files = {"purpose": "fine-tune", "file": open("mydata.jsonl", "rb")}

    response = requests.post(url, headers=headers, files=files)


@mod.action_class
class Actions:
    def image_describe_clipboard(prompt: str):
        """Describe an image on the clipboard"""

        prompt = (
            "I am a user with a visual impairment. Please describe to me what is in this image."
            if prompt == ""
            else prompt
        )

        base64_image = get_clipboard_image()

        TOKEN = get_token()

        # Getting the base64 string
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            # TODO not sure if this is the right number. Will depend a lot if we are trying to output HTML or just get a general description
            "max_tokens": 600,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

        # RESPONSE FORMAT (in case you don't GPT-4 access)
        """
         {'id': '$$REMOVED$$', 'object': 'chat.completion', 'created': 1707691631, 'model': 'gpt-4-1106-vision-preview', 'usage': {'prompt_tokens': 281, 'completion_tokens': 71, 'total_tokens': 352}, 'choices': [{'message': {'role': 'assistant', 'content': "The image is a close-up photo of a person's face. The individual appears to be a man with short hair, a slight stubble on the face, and a friendly expression"}, 'finish_reason': 'stop', 'index': 0}]}
        """

        response_dict = response.json()
        response_text = response_dict["choices"][0]["message"]["content"]
        print(response_text)
        return response_text

    def image_generate(prompt: str):
        """Generate an image from the provided text"""

        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        response = requests.post(url, headers=headers, json=data)

        # The response will be in JSON format, you can convert it to a Python dictionary using .json()
        response_dict = response.json()

        # RESPONSE FORMAT (in case you don't GPT-4 access)
        """
        {'created': $$REMOVED$$, 'data': [{'revised_prompt': 'Create a visually stunning image of a cat. The cat is domestic, with short, thick fur with brindle pattern.', 'url': '$$REMOVED$$'}]}
        """
        webbrowser.open(response_dict["data"][0]["url"])
        # TODO choose whether to save the image, save the url, or paste the image into the current window

    def image_apply(prompt: str):
        """Applies the prompt as a filter to the current image"""
        base64_image = get_clipboard_image()

        TOKEN = get_token()
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        response = requests.post(url, headers=headers, json=data)

        response_dict = response.json()

        webbrowser.open(response_dict["data"][0]["url"])
