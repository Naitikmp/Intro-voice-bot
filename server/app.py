import base64
from flask import Flask,request, send_file,jsonify,after_this_request
from flask_cors import CORS
from openai_client import get_response
from elevenlabs_tts import elevenlabs_tts
from gtts_tts import google_tts
import os
import traceback

app = Flask(__name__)
CORS(app, origins=["https://intro-voice-bot.vercel.app","http://localhost:5173"], supports_credentials=True)

import traceback  # add at the top if not already

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        print("Received JSON:", data)  # Debug: log the input

        user_input = data.get('message', '')
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        print("User input:", user_input)  # Debug

        bot_reply = get_response(user_input)
        print("Bot reply:", bot_reply)  # Debug

        # audio_stream = elevenlabs_tts(bot_reply)
        audio_stream = google_tts(text = bot_reply)
        print("TTS audio stream generated")  # Debug

        # Convert audio stream to base64
        audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
        print("Audio base64 encoded")  # Debug

        return jsonify({
            "text": bot_reply,
            "audio_base64": audio_base64
        })

    except Exception as e:
        print("Exception occurred in /api/chat:")
        traceback.print_exc()  # <- This prints full stack trace in Render logs
        return jsonify({'error': str(e)}), 500

    

if __name__ == "__main__":
    app.run(debug=True)