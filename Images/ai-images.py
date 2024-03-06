import base64
import time
import webbrowser

import requests
from talon import Module, clip, settings

from ..GPT.lib.gpt_helpers import get_token, notify
from ..GPT.lib.HTMLbuilder import Builder

mod = Module()

mod.setting("openDescriptionInBrowser", type=bool, default=True)
mod.setting("maxDescriptionTokens", type=int, default=300)

mod.list("descriptionPrompt", desc="Prompts for describing images")


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
            "max_tokens": settings.get("user.maxDescriptionTokens"),
        }
        notify("GPT Image Description Start...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

        match response.status_code:
            case 200:
                response_dict = response.json()
                response_text = response_dict["choices"][0]["message"]["content"]
                print(response_text)
                notify("Done")
                if settings.get("user.openDescriptionInBrowser"):
                    builder = Builder()
                    builder.title("Image Description")
                    builder.h1(f"AI Description for Image given at {time.ctime()}")
                    builder.p(response_text)
                    builder.base64_img(
                        base64_image, alt="Your image that was described"
                    )
                    builder.render()
                return response_text
            case _:
                print(response.json())
                notify("Error describing image")
                raise Exception("Error in describing image")

    def image_generate(prompt: str):
        """Generate an image from the provided text"""

        url = "https://api.openai.com/v1/images/generations"
        TOKEN = get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }

        response = requests.post(url, headers=headers, json=data)

        match response.status_code:
            case 200:
                response_dict = response.json()
                image_url = response_dict["data"][0]["url"]
                # TODO choose whether to save the image, save the url, or paste the image into the current window
                webbrowser.open(image_url)
            case _:
                print(response.json())
                notify("Error generating image")
                raise Exception("Error generating image")
