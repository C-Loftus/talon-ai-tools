import base64
import os
import webbrowser

import requests
from talon import Module, clip

mod = Module()


@mod.action_class
class Actions:
    def describe_clipboard():
        """Describe the image on the clipboard"""
        try:
            clipped_image = clip.image()
            if not clipped_image:
                print("No image found in clipboard")
                return

            data = clipped_image.encode().data()
            base64_image = base64.b64encode(data).decode("utf-8")
        except:
            print("Invalid image found in clipboard")
            return

        # OpenAI API Key
        api_key = os.environ["OPENAI_API_KEY"]

        # Getting the base64 string
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "I am a user with a visual impairment. Please describe to me what is in this image.",
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
            # TODO not sure if this is the right number
            "max_tokens": 300,
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

    def generate_image(prompt: str):
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
