import webbrowser

import requests
from talon import Module

from ..lib.modelHelpers import get_token, notify

mod = Module()


@mod.action_class
class Actions:
    def image_generate(prompt: str):
        """Generate an image from the provided text"""

        url = "https://api.openai.com/v1/images/generations"
        TOKEN = get_token()
        headers = {"Content-Type": "application/json"}
        # If the model endpoint is Azure, we need to use a different header
        if "azure.com" in url:
            headers["api-key"] = TOKEN
       # otherwise default to the standard header format for openai
        else:
            headers["Authorization"] = f"Bearer {TOKEN}"
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
