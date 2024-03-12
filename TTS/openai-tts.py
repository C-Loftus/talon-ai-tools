import json
import os
import time

import requests
from talon import Module, actions

from ..GPT.lib.gpt_helpers import get_token


#  Currently not publicly exposed given the latency and impractical cost
#  for using it for real time TTS interaction (better for audiobooks, etc.).
def _openai_tts(text: str):
    """text to speech with openai"""
    url = "https://api.openai.com/v1/audio/speech"
    TOKEN = get_token()

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        date = time.strftime("%Y-%m-%d-%H-%M-%S")
        with open(f"openai-speech-{date}.mp3", "wb") as f:
            f.write(response.content)
        print("Speech successfully saved to openai-speech.mp3")
    else:
        print(f"Error: {response.status_code}, {response.text}")
