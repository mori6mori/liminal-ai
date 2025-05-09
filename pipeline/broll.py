"""
broll.py - Generates B-roll footage for video content

This module creates visual content to accompany the audio narration.
It can generate placeholder videos or images based on the script content.
"""

import os
import random
import tempfile
from typing import List, Dict, Any, Optional, Union
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

class BRollGenerator:
    """
    Generates B-roll footage for video content using various methods.
    """
    
    def __init__(self, output_dir="output/video"):
        """
        Initialize the B-roll generator
        
        Args:
            output_dir (str): Directory to save output videos
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_placeholder_video(self, 
                                  duration: float, 
                                  title: str = None,
                                  keywords: List[str] = None,
                                  output_path: str = None) -> str:
        """
        Generate a placeholder video with the specified duration
        
        Args:
            duration (float): Duration of the video in seconds
            title (str, optional): Title to display in the video
            keywords (List[str], optional): Keywords to use for theming (not displayed)
            output_path (str, optional): Path to save the output video
            
        Returns:
            str: Path to the generated video
        """
        # Generate output path if not provided
        if not output_path:
            safe_title = "placeholder"
            if title:
                # Create a filename-safe version of the title
                safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())
            output_path = os.path.join(self.output_dir, f"{safe_title}.mp4")
        
        try:
            # Set video dimensions (vertical format for social media)
            height, width = 1920, 1080
            
            # Generate a simple color background with text
            bg_color = "black"
            text_color = "white"
            
            # Create text content - only use the title, not keywords
            text_content = title if title else "Placeholder Video"
            
            # Build FFmpeg command for generating a placeholder video
            command = [
                "ffmpeg",
                "-y",  # Overwrite output file if it exists
                "-f", "lavfi",  # Use libavfilter
                "-i", f"color=c={bg_color}:s={width}x{height}:d={duration}",  # Create color background
                "-vf", f"drawtext=text='{text_content}':fontcolor={text_color}:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/System/Library/Fonts/Helvetica.ttc",  # Add text
                "-c:v", "libx264",  # Video codec
                "-preset", "medium",  # Encoding preset
                "-pix_fmt", "yuv420p",  # Pixel format
                output_path
            ]
            
            # Execute FFmpeg command
            self.logger.info(f"Generating placeholder video with command: {' '.join(command)}")
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.logger.info(f"Successfully generated placeholder video: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error generating placeholder video: {e.stderr}")
            raise RuntimeError(f"Failed to generate placeholder video: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating placeholder video: {str(e)}")
            raise
    
    def generate_from_script(self, script: Dict[str, Any]) -> str:
        """
        Generate B-roll footage based on a script
        
        Args:
            script (Dict[str, Any]): Script dictionary with title, narration, etc.
            
        Returns:
            str: Path to the generated video
        """
        title = script.get("title", "Untitled Video")
        duration = script.get("estimated_duration_sec", 60)
        keywords = script.get("keywords", [])
        
        # Generate a filename based on the title
        safe_title = "".join(c if c.isalnum() else "_" for c in title.lower())
        output_path = os.path.join(self.output_dir, f"{safe_title}.mp4")
        
        # For now, just generate a placeholder video
        # In a real implementation, this would use more sophisticated methods
        return self.generate_placeholder_video(
            duration=duration,
            title=title,
            keywords=keywords,
            output_path=output_path
        )


if __name__ == "__main__":
    # Example usage
    generator = BRollGenerator()
    
    # Generate a simple placeholder video
    video_path = generator.generate_placeholder_video(
        duration=30,
        title="Sample B-Roll"
    )
    print(f"Placeholder video created: {video_path}")
    
    # Test with a script
    script = {
        "title": "Breaking the Matrix of Credentialism",
        "hook": "Morpheus was right: the rules were illusions.",
        "narration": "Schools taught us degrees = success. AI proves otherwise. The Matrix wasn't just a movie—it's our mental prison of 'you can't do X without Y.' High-agency people hack the system. They see credentials as speed bumps, not requirements. Like Neo realizing he could dodge bullets, founders now bypass traditional gatekeepers. The hardest part? Believing you're allowed to jump. AI's the red pill—swallow it, and watch the old world dissolve.",
        "cta": "Unplug from the system. Build anyway.",
        "keywords": [
          "#mindset",
          "#disruption",
          "#AIfuture"
        ],
        "estimated_duration_sec": 28
      }
    
    video_path = generator.generate_from_script(script)
    print(f"Script video created: {video_path}") 