import base64
from flask import Flask,request, send_file,jsonify,after_this_request
from flask_cors import CORS
from openai_client import get_response
from elevenlabs_tts import elevenlabs_tts
import os

app = Flask(__name__)
CORS(app, origins=["https://intro-voice-bot.vercel.app"], supports_credentials=True)

@app.route('/api/chat',methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message','')

    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        bot_reply = get_response(user_input)
        
        audio_stream = elevenlabs_tts(bot_reply)

        # Serve audio + text in one JSON object
        audio_base64 = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
        
        return jsonify({
                    "text": bot_reply,
                    "audio_base64": audio_base64
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)