import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, User, Bot, Loader2, VolumeX } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  audioBlob?: Blob;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);
  
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Initialize speech recognition
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsRecording(false);
      };

      recognitionRef.current.onerror = () => {
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Replace this with your actual API endpoint
      const response = await fetch('https://intro-voice-bot.onrender.com/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputText }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Handle audio blob from your API response format
        let audioBlob = null;
        if (data.audio_base64) {
          try {
            // Convert base64 audio data to blob
            const audioData = atob(data.audio_base64);
            const audioArray = new Uint8Array(audioData.length);
            for (let i = 0; i < audioData.length; i++) {
              audioArray[i] = audioData.charCodeAt(i);
            }
            audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
          } catch (error) {
            console.error('Error converting base64 audio:', error);
          }
        }

        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.text || "I received your message and I'm processing it.",
          sender: 'bot',
          timestamp: new Date(),
          audioBlob: audioBlob
        };

        setMessages(prev => [...prev, botMessage]);

        // Auto-play audio if available
        if (audioBlob) {
          playAudio(audioBlob, botMessage.id);
        }
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm having trouble connecting right now. Please try again.",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const playAudio = (audioBlob: Blob, messageId: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }

    const audioUrl = URL.createObjectURL(audioBlob);
    audioRef.current = new Audio(audioUrl);
    
    setCurrentPlayingId(messageId);
    setIsPlayingAudio(true);
    setAudioProgress(0);

    audioRef.current.onended = () => {
      setIsPlayingAudio(false);
      setAudioProgress(0);
      setCurrentPlayingId(null);
      URL.revokeObjectURL(audioUrl);
    };

    audioRef.current.ontimeupdate = () => {
      if (audioRef.current) {
        const progress = (audioRef.current.currentTime / audioRef.current.duration) * 100;
        setAudioProgress(progress);
      }
    };

    audioRef.current.play().catch(error => {
      console.error('Error playing audio:', error);
      setIsPlayingAudio(false);
      setCurrentPlayingId(null);
    });
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlayingAudio(false);
      setAudioProgress(0);
      setCurrentPlayingId(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center shadow-md">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className="text-center">
                <h1 className="text-xl font-semibold text-gray-900">Voice Intro AI Assistant</h1>
                <p className="text-sm text-gray-500">Powered by and for Naitik Patel</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Centered Input Area */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message or use voice..."
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all duration-200"
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
              />
            </div>
            
            {/* Voice Recording Button */}
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`p-3 rounded-xl transition-all duration-200 shadow-md ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-white hover:bg-gray-50 text-gray-600 border border-gray-200'
              }`}
              disabled={isLoading}
            >
              {isRecording ? (
                <MicOff className="w-5 h-5" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </button>

            {/* Send Button */}
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isLoading}
              className="p-3 bg-gray-800 hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {isRecording && (
            <div className="mt-4 flex items-center justify-center space-x-2 text-red-500 animate-fade-in">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium">Recording... Speak now</span>
            </div>
          )}

          {isLoading && (
            <div className="mt-4 flex items-center justify-center space-x-2 text-gray-600 animate-fade-in">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm font-medium">Processing your message...</span>
            </div>
          )}
        </div>

        {/* Audio Progress Indicator */}
        {isPlayingAudio && (
          <div className="mt-4 bg-white rounded-xl shadow-md border border-gray-100 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Volume2 className="w-5 h-5 text-gray-700 animate-pulse" />
                <span className="text-sm font-medium text-gray-700">Playing audio response</span>
                <div className="flex space-x-1">
                  <div className="audio-wave"></div>
                  <div className="audio-wave"></div>
                  <div className="audio-wave"></div>
                  <div className="audio-wave"></div>
                </div>
              </div>
              <button
                onClick={stopAudio}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <VolumeX className="w-4 h-4 text-gray-500" />
              </button>
            </div>
            <div className="mt-3 w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gray-700 transition-all duration-100 rounded-full"
                style={{ width: `${audioProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Chat Messages - Below input */}
      {messages.length > 0 && (
        <div className="max-w-4xl mx-auto px-6 pb-8">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6 text-center">Conversation History</h2>
            <div className="space-y-6 max-h-96 overflow-y-auto">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in message-enter`}
                >
                  <div className={`flex items-start space-x-3 max-w-xs lg:max-w-md`}>
                    {message.sender === 'bot' && (
                      <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div
                      className={`px-4 py-3 rounded-2xl shadow-md hover-lift ${
                        message.sender === 'user'
                          ? 'bg-gray-800 text-white ml-auto'
                          : 'bg-gray-100 border border-gray-200 text-gray-900'
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.text}</p>
                      <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-gray-300' : 'text-gray-500'}`}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      {message.audioBlob && (
                        <button
                          onClick={() => playAudio(message.audioBlob!, message.id)}
                          className={`mt-2 flex items-center space-x-2 text-xs rounded-full px-3 py-1 transition-colors ${
                            currentPlayingId === message.id
                              ? 'bg-gray-200 text-gray-800'
                              : 'bg-white hover:bg-gray-50 text-gray-600 border border-gray-200'
                          }`}
                        >
                          <Volume2 className="w-3 h-3" />
                          <span>{currentPlayingId === message.id ? 'Playing...' : 'Play Audio'}</span>
                        </button>
                      )}
                    </div>
                    {message.sender === 'user' && (
                      <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                        <User className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>
      )}

      {/* Welcome Message when no conversations */}
      {messages.length === 0 && (
        <div className="max-w-4xl mx-auto px-6 pb-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
              <Bot className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Welcome to Voice based AI bot</h2>
            <p className="text-gray-600 mb-6">Start a conversation by typing a message or using voice input above.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
              <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover-lift">
                <Mic className="w-6 h-6 text-gray-700 mb-2" />
                <h3 className="font-medium text-gray-900 mb-1">Voice Input</h3>
                <p className="text-sm text-gray-600">Click the microphone to speak</p>
              </div>
              <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover-lift">
                <Volume2 className="w-6 h-6 text-gray-700 mb-2" />
                <h3 className="font-medium text-gray-900 mb-1">Audio Responses</h3>
                <p className="text-sm text-gray-600">Get audio replies automatically</p>
              </div>
              <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover-lift">
                <Bot className="w-6 h-6 text-gray-700 mb-2" />
                <h3 className="font-medium text-gray-900 mb-1">Smart AI</h3>
                <p className="text-sm text-gray-600">Intelligent conversation partner</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;