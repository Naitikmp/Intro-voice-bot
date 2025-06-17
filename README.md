# Voice Intro AI Bot

A modern, interactive AI assistant that supports both text and voice-based communication. The application features a beautiful React-based frontend and a powerful Python backend that integrates OpenAI's GPT model and ElevenLabs' text-to-speech capabilities.

## Features

- 🎙️ **Voice Input**: Record your voice to communicate with the AI
- 🔊 **Voice Output**: Receive natural-sounding voice responses through ElevenLabs TTS
- 💬 **Text Chat**: Traditional text-based chat interface
- 🎨 **Modern UI**: Beautiful, responsive design with smooth animations
- 🔄 **Real-time Processing**: Instant responses with loading states
- 🌐 **Full Stack**: React (TypeScript) frontend + Python Flask backend

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Lucide React for icons
- Web Speech API for voice input

### Backend
- Flask (Python)
- OpenAI API for chat responses
- ElevenLabs API for text-to-speech
- CORS support for cross-origin requests

## Prerequisites

- Node.js (v16 or higher)
- Python 3.10 or higher
- OpenAI API key
- ElevenLabs API key

## Environment Setup

1. Clone the repository
2. Create a `.env` file in the server directory with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   VOICE_ID=your_preferred_voice_id
   ```

## Installation

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

### Backend Setup
```bash
cd server
pip install -r requirements.txt
python app.py
```

## Project Structure

```
.
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── App.tsx        # Main application component
│   │   ├── main.tsx       # Entry point
│   │   └── index.css      # Global styles
│   ├── package.json
│   └── vite.config.ts
│
└── server/                 # Backend Flask application
    ├── app.py             # Main Flask application
    ├── config.py          # Configuration and environment variables
    ├── openai_client.py   # OpenAI integration
    ├── elevenlabs_tts.py  # ElevenLabs TTS integration
    └── requirements.txt    # Python dependencies
```

## Usage

1. Start the frontend development server: `npm run dev` in the client directory
2. Start the backend server: `python app.py` in the server directory
3. Open your browser to `http://localhost:5173`
4. Start chatting with the AI using either text or voice input
5. Click the microphone icon to start/stop voice recording
6. Click the send button or press Enter to send your message
7. Receive text and audio responses from the AI

## Key Features Explained

### Voice Input
- Uses the Web Speech API for voice recognition
- Supports continuous recording with interim results
- Automatically converts speech to text

### AI Response
- Processes user input through OpenAI's GPT model
- Maintains conversation context
- Generates natural, contextual responses

### Text-to-Speech
- Converts AI responses to natural-sounding speech
- Supports multiple voices through ElevenLabs
- Automatic playback with progress tracking

### User Interface
- Modern, responsive design
- Real-time feedback and loading states
- Audio visualization during playback
- Message history with timestamps

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- OpenAI for the GPT API
- ElevenLabs for the Text-to-Speech API
- The React and Flask communities for their excellent documentation
