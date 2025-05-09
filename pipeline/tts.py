"""
tts.py - Converts script to voiceover audio

Input: Script with segments
Output: Voiceover audio files (MP3)
"""

import os
import json
import tempfile
from typing import Dict, List, Any
import requests
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
class TextToSpeech:
    def __init__(self, api_key=ELEVENLABS_API_KEY, voice=ELEVENLABS_VOICE_ID):
        """
        Initialize the TTS engine
        
        Args:
            api_key (str, optional): API key for TTS service
            voice (str): Voice ID to use
        """
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        self.voice = voice
        self.output_dir = "output/audio"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_voiceover(self, script: dict) -> dict:
        """
        Generate voiceover for the script using ElevenLabs API
        
        Args:
            script (dict): Script with text content
            
        Returns:
            dict: Voiceover data with audio file path
        """

        text = script["narration"]
        title = script["title"]
            # Generate audio for the text
        audio_file = self._generate_audio(text, title)
            
            # Get duration of the audio file
        audio = AudioSegment.from_mp3(audio_file)
        duration = len(audio) / 1000  # Convert ms to seconds
            
        return {
            "title": script.get("title", ""),
            "full_audio": audio_file,
            "duration": duration,
            "text": script
        }
            
    
    def _generate_audio(self, text: str, title: str) -> str:
        """
        Generate audio for a text segment using ElevenLabs API
        
        Args:
            text (str): Text to convert to speech
            filename (str): Base filename for the output
            
        Returns:
            str: Path to the generated audio file
        """
        filename = title
        # Generate a unique filename based on text content if not provided
        if not filename:
            # Create a pseudo-filename from the first few words of the text
            pseudo_filename = "_".join(text.split()[:3]).lower()
            # Remove any non-alphanumeric characters
            pseudo_filename = "".join(c for c in pseudo_filename if c.isalnum() or c == "_")
            filename = f"audio_{pseudo_filename}"
        
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        # ElevenLabs API endpoint
        url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        # Replace with actual voice ID (default to "Rachel" if not specified)
        voice_id = self.voice
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": os.getenv("ELEVENLABS_MODEL_ID"),
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.8,
                "use_speaker_boost": True,
                "speed": 1.1
            }
        }
        
        try:
            response = requests.post(
                url.format(voice_id=voice_id),
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"Error from ElevenLabs API: {response.status_code} - {response.text}")
                raise Exception(f"ElevenLabs API error: {response.status_code}")
                
        except Exception as e:
            print(f"Failed to generate audio: {e}")
            raise
 

if __name__ == "__main__":
    tts = TextToSpeech(api_key=os.getenv("ELEVENLABS_API_KEY"), voice=os.getenv("ELEVENLABS_VOICE_ID"))
    
    script = {
        "title": "How AI is Creating 1-Person Billion-Dollar Companies",
        "hook": "Forget everything you know about startups. AI is rewriting the rules of business—permanently.",
        "narration": "Sam Altman predicted a 1-person billion-dollar company. Now, it's happening—not just because of AI, but because of a new breed of high-agency founders. These aren't your typical CEOs. They're rebels who build without permission, using AI to replace entire teams. No sales, no HR, just raw hustle and machines. The old world demanded degrees and decades of specialization. AI flips the script: now, it's about who acts fastest. Midjourney runs $500M/year with 40 people. Solo founders are doubling. The future belongs to those who 'just do things'—no rulebook needed.",
        "cta": "Stop waiting. Start building. AI's your co-founder now.",
        "keywords": [
            "#AIrevolution",
            "#startups",
            "#futureofwork",
            "#hustle"
        ]
    }
    voiceover = tts.generate_voiceover(script)
    print(json.dumps(voiceover, indent=2)) 