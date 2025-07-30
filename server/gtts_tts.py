import io
import os
import re
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def google_tts(text: str, lang: str = 'en', slow: bool = False) -> io.BytesIO:
    """
    Google Text-to-Speech using gTTS (free service) with support for long text
    
    Args:
        text (str): Text to convert to speech (any length)
        lang (str): Language code (default: 'en')
        slow (bool): Speak slowly (default: False)
    
    Returns:
        io.BytesIO: Audio content as BytesIO object
        
    Raises:
        Exception: If TTS generation fails
    """
    try:
        from gtts import gTTS
    except ImportError:
        raise Exception("gTTS not installed. Install with: pip install gtts")
    
    # Clean text
    text = _clean_text(text)
    if not text.strip():
        raise Exception("Empty text provided for TTS")
    
    try:
        # Check if text is short enough for single request
        if len(text) <= 100:
            logger.info(f"Generating Google TTS for short text: '{text[:50]}...'")
            tts = gTTS(text=text, lang=lang, slow=slow)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer
        
        # Handle long text with chunking
        logger.info(f"Generating Google TTS for long text ({len(text)} characters)")
        return _generate_long_text_tts(text, lang, slow)
        
    except Exception as e:
        raise Exception(f"Google TTS API error: {str(e)}")


def google_cloud_tts(text: str, language_code: str = "en-US", voice_name: Optional[str] = None) -> io.BytesIO:
    """
    Google Cloud Text-to-Speech with support for long text
    
    Args:
        text (str): Text to convert to speech (any length)
        language_code (str): Language code (default: "en-US")
        voice_name (str, optional): Specific voice name
    
    Returns:
        io.BytesIO: Audio content as BytesIO object
        
    Raises:
        Exception: If TTS generation fails
    """
    try:
        from google.cloud import texttospeech
    except ImportError:
        raise Exception("Google Cloud TTS not installed. Install with: pip install google-cloud-texttospeech")
    
    # Check for credentials
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS') and not os.getenv('GOOGLE_CLOUD_PROJECT'):
        raise Exception("Google Cloud credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
    
    # Clean text
    text = _clean_text(text)
    if not text.strip():
        raise Exception("Empty text provided for TTS")
    
    try:
        # Google Cloud TTS has a limit of 5000 characters
        if len(text) <= 5000:
            logger.info(f"Generating Google Cloud TTS for text: '{text[:50]}...'")
            return _generate_single_cloud_tts(text, language_code, voice_name)
        
        # Handle long text with chunking
        logger.info(f"Generating Google Cloud TTS for long text ({len(text)} characters)")
        return _generate_long_cloud_tts(text, language_code, voice_name)
        
    except Exception as e:
        raise Exception(f"Google Cloud TTS API error: {str(e)}")


def _generate_long_text_tts(text: str, lang: str, slow: bool) -> io.BytesIO:
    """Generate TTS for long text by chunking and concatenating audio"""
    from gtts import gTTS
    
    # Split text into chunks
    chunks = _split_text_smart(text, max_length=100)
    logger.info(f"Split text into {len(chunks)} chunks")
    
    audio_segments = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        logger.info(f"Processing chunk {i+1}/{len(chunks)}: '{chunk[:30]}...'")
        
        try:
            tts = gTTS(text=chunk, lang=lang, slow=slow)
            chunk_buffer = io.BytesIO()
            tts.write_to_fp(chunk_buffer)
            chunk_buffer.seek(0)
            audio_segments.append(chunk_buffer.getvalue())
            
        except Exception as e:
            logger.warning(f"Failed to generate TTS for chunk {i+1}: {e}")
            continue
    
    if not audio_segments:
        raise Exception("Failed to generate audio for any text chunks")
    
    # Concatenate audio segments
    return _concatenate_audio_segments(audio_segments)


def _generate_long_cloud_tts(text: str, language_code: str, voice_name: Optional[str]) -> io.BytesIO:
    """Generate Google Cloud TTS for long text by chunking"""
    # Split text into chunks (Google Cloud limit is 5000 chars)
    chunks = _split_text_smart(text, max_length=4500)  # Leave some buffer
    logger.info(f"Split text into {len(chunks)} chunks")
    
    audio_segments = []
    
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        logger.info(f"Processing chunk {i+1}/{len(chunks)}: '{chunk[:30]}...'")
        
        try:
            chunk_audio = _generate_single_cloud_tts(chunk, language_code, voice_name)
            audio_segments.append(chunk_audio.getvalue())
            
        except Exception as e:
            logger.warning(f"Failed to generate TTS for chunk {i+1}: {e}")
            continue
    
    if not audio_segments:
        raise Exception("Failed to generate audio for any text chunks")
    
    # Concatenate audio segments
    return _concatenate_audio_segments(audio_segments)


def _generate_single_cloud_tts(text: str, language_code: str, voice_name: Optional[str]) -> io.BytesIO:
    """Generate single Google Cloud TTS request"""
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    
    voice_params = {
        "language_code": language_code,
        "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL
    }
    
    if voice_name:
        voice_params["name"] = voice_name
        
    voice = texttospeech.VoiceSelectionParams(**voice_params)
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.1
    )
    
    response = client.synthesize_speech(
        input=synthesis_input, 
        voice=voice, 
        audio_config=audio_config
    )
    
    return io.BytesIO(response.audio_content)


def _split_text_smart(text: str, max_length: int) -> List[str]:
    """
    Split text intelligently preserving sentence boundaries
    
    Args:
        text (str): Text to split
        max_length (int): Maximum length per chunk
        
    Returns:
        List[str]: List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for sentence in sentences:
        # If single sentence is too long, split by clauses/commas
        if len(sentence) > max_length:
            sub_chunks = _split_long_sentence(sentence, max_length)
            for sub_chunk in sub_chunks:
                if len(current_chunk + " " + sub_chunk) <= max_length:
                    current_chunk = (current_chunk + " " + sub_chunk).strip()
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sub_chunk
        else:
            # Check if adding this sentence exceeds limit
            if len(current_chunk + " " + sentence) <= max_length:
                current_chunk = (current_chunk + " " + sentence).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def _split_long_sentence(sentence: str, max_length: int) -> List[str]:
    """Split a long sentence by commas, semicolons, and conjunctions"""
    if len(sentence) <= max_length:
        return [sentence]
    
    # Split by various punctuation and conjunctions
    parts = re.split(r'([,;]|\s+(?:and|but|or|so|yet|for|nor)\s+)', sentence)
    
    chunks = []
    current_chunk = ""
    
    for part in parts:
        if len(current_chunk + part) <= max_length:
            current_chunk += part
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If even a single part is too long, split by words
            if len(part) > max_length:
                word_chunks = _split_by_words(part, max_length)
                chunks.extend(word_chunks)
                current_chunk = ""
            else:
                current_chunk = part
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if chunk.strip()]


def _split_by_words(text: str, max_length: int) -> List[str]:
    """Split text by words as last resort"""
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        if len(current_chunk + " " + word) <= max_length:
            current_chunk = (current_chunk + " " + word).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def _concatenate_audio_segments(audio_segments: List[bytes]) -> io.BytesIO:
    """
    Concatenate multiple audio segments into single audio file
    
    Args:
        audio_segments (List[bytes]): List of audio data
        
    Returns:
        io.BytesIO: Combined audio
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        # Fallback: simple concatenation (less optimal but works)
        logger.warning("pydub not available, using simple concatenation")
        return _simple_audio_concatenation(audio_segments)
    
    try:
        # Use pydub for proper audio concatenation
        combined = AudioSegment.empty()
        
        for i, segment_data in enumerate(audio_segments):
            try:
                audio_segment = AudioSegment.from_mp3(io.BytesIO(segment_data))
                combined += audio_segment
                
                # Add small pause between segments (50ms)
                if i < len(audio_segments) - 1:
                    pause = AudioSegment.silent(duration=50)
                    combined += pause
                    
            except Exception as e:
                logger.warning(f"Failed to process audio segment {i}: {e}")
                continue
        
        # Export combined audio
        output_buffer = io.BytesIO()
        combined.export(output_buffer, format="mp3")
        output_buffer.seek(0)
        
        logger.info(f"Successfully concatenated {len(audio_segments)} audio segments")
        return output_buffer
        
    except Exception as e:
        logger.warning(f"pydub concatenation failed: {e}, using simple concatenation")
        return _simple_audio_concatenation(audio_segments)


def _simple_audio_concatenation(audio_segments: List[bytes]) -> io.BytesIO:
    """Simple audio concatenation without pydub (fallback)"""
    combined_audio = b"".join(audio_segments)
    return io.BytesIO(combined_audio)


def _clean_text(text: str) -> str:
    """Clean and prepare text for TTS"""
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Remove or replace problematic characters
    text = text.replace('"', "'")
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    
    # Remove multiple punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    return text


def get_available_voices(language_code: str = "en-US") -> list:
    """Get available voices for Google Cloud TTS"""
    try:
        from google.cloud import texttospeech
    except ImportError:
        raise Exception("Google Cloud TTS not installed")
    
    try:
        client = texttospeech.TextToSpeechClient()
        voices = client.list_voices(language_code=language_code)
        
        voice_names = []
        for voice in voices.voices:
            voice_names.append(voice.name)
            
        return voice_names
        
    except Exception as e:
        raise Exception(f"Failed to get available voices: {str(e)}")


def test_google_tts():
    """Test function with both short and long text"""
    short_text = "Hello, this is a short test."
    long_text = """
    This is a much longer text that will test the chunking functionality of our Google TTS implementation. 
    It contains multiple sentences and should be split into appropriate chunks for processing. 
    The system should handle this automatically and concatenate the audio segments back together seamlessly. 
    This way we can convert any length of text to speech without hitting API limits. 
    The chunking respects sentence boundaries to maintain natural speech flow.
    """
    
    print("Testing Google TTS with short text...")
    try:
        audio1 = google_tts(short_text)
        print(f"✓ Short text TTS successful - Audio size: {len(audio1.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Short text TTS failed: {e}")
    
    print("\nTesting Google TTS with long text...")
    try:
        audio2 = google_tts(long_text)
        print(f"✓ Long text TTS successful - Audio size: {len(audio2.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Long text TTS failed: {e}")
    
    print("\nTesting Google Cloud TTS...")
    try:
        audio3 = google_cloud_tts(long_text)
        print(f"✓ Google Cloud TTS successful - Audio size: {len(audio3.getvalue())} bytes")
    except Exception as e:
        print(f"✗ Google Cloud TTS failed: {e}")


if __name__ == "__main__":
    test_google_tts()