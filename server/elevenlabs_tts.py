import io
import requests
import uuid
from config import ELEVENLABS_API_KEY, VOICE_ID

def elevenlabs_tts(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    text = f"<speak><prosody rate='fast'>{text}</prosody></speak>"
    payload = {
        "text" : text,
        "voice_settings":{
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url,headers=headers,json=payload)
    if response.status_code == 200:
        return io.BytesIO(response.content)
        # filename = f"audio_{uuid.uuid4()}.mp3"
        # with open(filename,"wb") as f:
        #     f.write(response.content)
        # return filename
    else:
        raise Exception(f"ElevenLabs TTS API error: {response.status_code} — {response.text}")