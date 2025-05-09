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

class TextToSpeech:
    def __init__(self, api_key=None, voice="en-US-Neural2-F"):
        """
        Initialize the TTS engine
        
        Args:
            api_key (str, optional): API key for TTS service
            voice (str): Voice ID to use
        """
        self.api_key = api_key or os.environ.get("TTS_API_KEY")
        self.voice = voice
        self.output_dir = "output/audio"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_voiceover(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate voiceover for the entire script
        
        Args:
            script (dict): Script with segments
            
        Returns:
            dict: Voiceover data with audio file paths
        """
        try:
            segments = script.get("segments", [])
            audio_segments = []
            combined_audio = None
            
            for i, segment in enumerate(segments):
                # Generate audio for this segment
                audio_file = self._generate_segment_audio(segment["text"], f"segment_{i}")
                
                # Get duration of the audio file
                audio = AudioSegment.from_mp3(audio_file)
                duration = len(audio) / 1000  # Convert ms to seconds
                
                # Add to list of segments
                audio_segments.append({
                    "id": i,
                    "text": segment["text"],
                    "audio_file": audio_file,
                    "duration": duration
                })
                
                # Combine with previous segments
                if combined_audio is None:
                    combined_audio = audio
                else:
                    combined_audio += audio
            
            # Save the combined audio
            combined_file = os.path.join(self.output_dir, "full_voiceover.mp3")
            combined_audio.export(combined_file, format="mp3")
            
            # Calculate timing information
            current_time = 0
            for segment in audio_segments:
                segment["start_time"] = current_time
                segment["end_time"] = current_time + segment["duration"]
                current_time += segment["duration"]
            
            return {
                "title": script.get("title", ""),
                "full_audio": combined_file,
                "duration": current_time,
                "segments": audio_segments
            }
            
        except Exception as e:
            print(f"Error generating voiceover: {e}")
            return {"error": str(e)}
    
    def _generate_segment_audio(self, text, segment_id):
        """
        Generate audio for a single segment
        
        Args:
            text (str): Text to convert to speech
            segment_id (str): Identifier for the segment
            
        Returns:
            str: Path to the generated audio file
        """
        # This is a placeholder for the actual TTS API call
        # In a real implementation, you would call your TTS service here
        
        if self.api_key:
            # Example using a hypothetical TTS API
            try:
                response = self._call_tts_api(text)
                
                # Save the audio to a file
                output_file = os.path.join(self.output_dir, f"{segment_id}.mp3")
                with open(output_file, "wb") as f:
                    f.write(response.content)
                
                return output_file
                
            except Exception as e:
                print(f"Error calling TTS API: {e}")
                # Fall back to the mock implementation
                return self._mock_tts(text, segment_id)
        else:
            # Use mock implementation for testing
            return self._mock_tts(text, segment_id)
    
    def _call_tts_api(self, text):
        """
        Call the TTS API to convert text to speech
        
        Args:
            text (str): Text to convert
            
        Returns:
            Response: API response
        """
        # This is a placeholder - replace with your actual TTS API
        url = "https://api.example.com/tts"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "voice": self.voice,
            "format": "mp3"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response
    
    def _mock_tts(self, text, segment_id):
        """
        Create a mock audio file for testing
        
        Args:
            text (str): Text to convert
            segment_id (str): Identifier for the segment
            
        Returns:
            str: Path to the generated audio file
        """
        # Create a silent audio file with duration based on text length
        # 3 words per second is a reasonable speaking rate
        word_count = len(text.split())
        duration_ms = max(1000, word_count * 333)  # At least 1 second
        
        # Create silent audio
        audio = AudioSegment.silent(duration=duration_ms)
        
        # Save to file
        output_file = os.path.join(self.output_dir, f"{segment_id}.mp3")
        audio.export(output_file, format="mp3")
        
        return output_file


if __name__ == "__main__":
    # Example usage
    # tts = TextToSpeech()
    
    # Sample script
    # script = {
    #     "title": "Climate Change Explained",
    #     "segments": [
    #         {"text": "Climate change is affecting our planet in unprecedented ways.", "duration": 5},
    #         {"text": "Human activities are the main driver of these changes.", "duration": 4}
    #     ]
    # }
    
    # Generate voiceover
    # voiceover = tts.generate_voiceover(script)
    # print(json.dumps(voiceover, indent=2)) 