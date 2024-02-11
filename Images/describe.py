from talon import Module, clip
import requests, os

mod = Module()

@mod.action_class
class Actions:
    def describe_clipboard():
        """Describe the image on the clipboard"""
        base64_image = clip.image().encode().data

        # OpenAI API Key
        api_key = os.environ["OPENAI_API_KEY"]

        # Getting the base64 string
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
        }

        payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "I am a user with a visual impairment. Please describe to me what is in this image."
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
            }
        ],
        # TODO not sure if this is the right number
        "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        print(response.json())

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
        print(response_dict)
        # TODO choose whether to save the image, save the url, or paste the image into the current window
    