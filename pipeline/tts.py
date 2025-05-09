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
ASSEMBLY_API_KEY = os.getenv("ASSEMBLY_API_KEY")

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
    
    def generate_caption(self, audio_file: str) -> str:
        """
        Generate captions for an audio file using AssemblyAI
        
        Args:
            audio_file (str): Path to the audio file
            
        Returns:
            str: Path to the generated SRT caption file
        """
        # Check if AssemblyAI API key is available
        assembly_api_key = ASSEMBLY_API_KEY
        if not assembly_api_key:
            raise ValueError("AssemblyAI API key not found in environment variables")
        
        # AssemblyAI API endpoints
        upload_endpoint = "https://api.assemblyai.com/v2/upload"
        transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
        
        headers_auth = {
            "authorization": assembly_api_key
        }
        
        headers_json = {
            "authorization": assembly_api_key,
            "content-type": "application/json"
        }
        
        print(f"Uploading audio file: {audio_file}")
        
        # Upload the audio file
        with open(audio_file, "rb") as f:
            upload_response = requests.post(
                upload_endpoint,
                headers=headers_auth,
                data=f
            )
        
        if upload_response.status_code != 200:
            raise Exception(f"Error uploading file: {upload_response.text}")
        
        upload_url = upload_response.json()["upload_url"]
        print(f"File uploaded successfully. URL: {upload_url}")
        
        # Request transcription with word-level timestamps
        transcript_request = {
            "audio_url": upload_url
        }
        
        print(f"Requesting transcription with payload: {json.dumps(transcript_request)}")
        
        transcript_response = requests.post(
            transcript_endpoint,
            json=transcript_request,
            headers=headers_json
        )
        
        if transcript_response.status_code != 200:
            print(f"Full response: {transcript_response.text}")
            raise Exception(f"Error requesting transcription: {transcript_response.text}")
        
        transcript_id = transcript_response.json()["id"]
        print(f"Transcription requested. ID: {transcript_id}")
        
        # Poll for completion
        polling_endpoint = f"{transcript_endpoint}/{transcript_id}"
        
        while True:
            polling_response = requests.get(polling_endpoint, headers=headers_auth)
            
            if polling_response.status_code != 200:
                raise Exception(f"Error polling for transcription: {polling_response.text}")
            
            status = polling_response.json()["status"]
            print(f"Transcription status: {status}")
            
            if status == "completed":
                break
            elif status == "error":
                raise Exception(f"Transcription error: {polling_response.json()}")
            
            import time
            time.sleep(3)
        
        # Get the words with timestamps
        transcript_result = polling_response.json()
        words = transcript_result.get("words", [])
        
        if not words:
            raise Exception("No word-level timestamps found in the transcript")
        
        print(f"Transcription completed with {len(words)} words")
        
        # Create SRT file
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        srt_file = os.path.join(self.output_dir, f"{base_filename}.srt")
        
        # Convert timestamps to SRT format
        def format_time(ms):
            """Convert milliseconds to SRT time format (HH:MM:SS,mmm)"""
            s, ms = divmod(ms, 1000)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        # Group words into lines (approximately 7 words per line)
        lines = []
        current_line = []
        word_count = 0
        
        for word in words:
            current_line.append(word)
            word_count += 1
            
            if word_count >= 7 or word.get("text", "").strip().endswith((".", "!", "?")):
                lines.append(current_line)
                current_line = []
                word_count = 0
        
        # Add any remaining words
        if current_line:
            lines.append(current_line)
        
        # Write SRT file
        with open(srt_file, "w") as f:
            for i, line in enumerate(lines, 1):
                if not line:
                    continue
                    
                start_time = line[0].get("start")
                end_time = line[-1].get("end")
                
                if start_time is None or end_time is None:
                    continue
                
                # Format the line text
                text = " ".join(word.get("text", "") for word in line)
                
                # Write SRT entry
                f.write(f"{i}\n")
                f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                f.write(f"{text}\n\n")
        
        print(f"SRT file created: {srt_file}")
        return srt_file

        
        

if __name__ == "__main__":

    tts = TextToSpeech(api_key=os.getenv("ELEVENLABS_API_KEY"), voice=os.getenv("ELEVENLABS_VOICE_ID"))
    
    # script = {
    #     "title": "How AI is Creating 1-Person Billion-Dollar Companies",
    #     "hook": "Forget everything you know about startups. AI is rewriting the rules of business—permanently.",
    #     "narration": "Sam Altman predicted a 1-person billion-dollar company. Now, it's happening—not just because of AI, but because of a new breed of high-agency founders. These aren't your typical CEOs. They're rebels who build without permission, using AI to replace entire teams. No sales, no HR, just raw hustle and machines. The old world demanded degrees and decades of specialization. AI flips the script: now, it's about who acts fastest. Midjourney runs $500M/year with 40 people. Solo founders are doubling. The future belongs to those who 'just do things'—no rulebook needed.",
    #     "cta": "Stop waiting. Start building. AI's your co-founder now.",
    #     "keywords": [
    #         "#AIrevolution",
    #         "#startups",
    #         "#futureofwork",
    #         "#hustle"
    #     ]
    # }
    # voiceover = tts.generate_voiceover(script)
    # print(json.dumps(voiceover, indent=2)) 

    caption = tts.generate_caption("output/audio/credit.mp3")
    print(caption)
