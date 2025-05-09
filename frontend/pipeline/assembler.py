"""
assembler.py - Combines voiceover and B-Roll into final video

Input: Voiceover audio and B-Roll video clips
Output: Final assembled MP4 video
"""

import os
import json
import subprocess
from typing import Dict, List, Any
import tempfile
import shutil

class VideoAssembler:
    def __init__(self):
        """
        Initialize the video assembler
        """
        self.output_dir = "output/final"
        self.temp_dir = "temp"
        
        # Create output and temp directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Check if FFmpeg is installed
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: FFmpeg not found. Video assembly may fail.")
    
    def assemble_video(self, script: Dict[str, Any], voiceover: Dict[str, Any], broll: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble the final video from voiceover and B-Roll
        
        Args:
            script (dict): Script with segments
            voiceover (dict): Voiceover data with audio files
            broll (dict): B-Roll data with video files
            
        Returns:
            dict: Final video data
        """
        try:
            # Create a unique output filename
            timestamp = int(os.path.getmtime(voiceover["full_audio"]))
            output_file = os.path.join(self.output_dir, f"final_video_{timestamp}.mp4")
            
            # Create a temporary file for the FFmpeg command list
            concat_file = os.path.join(self.temp_dir, f"concat_{timestamp}.txt")
            
            # Prepare segments for assembly
            with open(concat_file, "w") as f:
                for i, segment in enumerate(voiceover["segments"]):
                    # Find the corresponding B-Roll clip
                    broll_clip = next((clip for clip in broll["clips"] if clip["id"] == segment["id"]), None)
                    
                    if broll_clip and os.path.exists(broll_clip["video_file"]):
                        # Create a temporary video with the audio segment
                        temp_output = os.path.join(self.temp_dir, f"segment_{i}.mp4")
                        
                        # Use FFmpeg to add audio to the B-Roll clip
                        self._add_audio_to_video(
                            broll_clip["video_file"],
                            segment["audio_file"],
                            temp_output
                        )
                        
                        # Add to the concat list
                        f.write(f"file '{os.path.abspath(temp_output)}'\n")
                    else:
                        print(f"Warning: Missing B-Roll for segment {i}")
            
            # Concatenate all segments into the final video
            self._concatenate_videos(concat_file, output_file)
            
            # Clean up temporary files
            # self._cleanup_temp_files()
            
            return {
                "title": script.get("title", ""),
                "video_file": output_file,
                "duration": voiceover["duration"]
            }
            
        except Exception as e:
            print(f"Error assembling video: {e}")
            return {"error": str(e)}
    
    def _add_audio_to_video(self, video_file, audio_file, output_file):
        """
        Add audio to a video file
        
        Args:
            video_file (str): Path to the video file
            audio_file (str): Path to the audio file
            output_file (str): Path to the output file
        """
        cmd = [
            "ffmpeg",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_file
        ]
        
        subprocess.run(cmd) 