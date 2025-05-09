import os
import subprocess
import logging
from typing import Optional, Dict, Any

class VideoAssembler:
    """
    Assembles final video from script, audio, video, and subtitle components.
    Uses FFmpeg for media processing.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the VideoAssembler.
        
        Args:
            output_dir: Directory where assembled videos will be saved
        """
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def assemble(self, 
                video_path: str, 
                audio_path: str, 
                subtitle_path: Optional[str] = None,
                script_data: Optional[Dict[str, Any]] = None,
                output_filename: Optional[str] = None) -> str:
        """
        Assemble the final video by combining video, audio, and subtitles.
        
        Args:
            video_path: Path to the video file
            audio_path: Path to the audio file
            subtitle_path: Path to the SRT subtitle file (optional)
            script_data: Dictionary containing script metadata (optional)
            output_filename: Name for the output file (optional)
            
        Returns:
            Path to the assembled video file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        if subtitle_path and not os.path.exists(subtitle_path):
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
        
        # Generate output filename if not provided
        if not output_filename:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_filename = f"{base_name}_assembled.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Build FFmpeg command
        command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i", video_path,  # Input video
            "-i", audio_path,  # Input audio
        ]
        
        # Add subtitle input if provided
        if subtitle_path:
            command.extend([
                "-vf", f"subtitles={subtitle_path}:force_style='Alignment=2,MarginV=75,FontSize=16,FontName=Arial,Bold=1'",  # Increased vertical margin to move captions lower
            ])
        
        # Add output file and encoding parameters
        command.extend([
            "-c:v", "libx264",  # Video codec
            "-c:a", "aac",      # Audio codec
            "-map", "0:v:0",    # Map video from first input
            "-map", "1:a:0",    # Map audio from second input
            "-shortest",        # Finish encoding when the shortest input stream ends
            output_path
        ])
        
        # Execute FFmpeg command
        try:
            self.logger.info(f"Assembling video with command: {' '.join(command)}")
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.logger.info(f"Successfully assembled video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error assembling video: {e.stderr}")
            raise RuntimeError(f"Failed to assemble video: {e.stderr}")
    
    def add_metadata(self, video_path: str, metadata: Dict[str, Any]) -> str:
        """
        Add metadata to the assembled video file.
        
        Args:
            video_path: Path to the video file
            metadata: Dictionary of metadata to add
            
        Returns:
            Path to the video file with metadata
        """
        # Implementation for adding metadata if needed
        # This could use FFmpeg's metadata options or another approach
        return video_path


def assemble_video(video_path: str, 
                  audio_path: str, 
                  subtitle_path: Optional[str] = None,
                  script_data: Optional[Dict[str, Any]] = None,
                  output_dir: str = "output",
                  output_filename: Optional[str] = None) -> str:
    """
    Convenience function to assemble a video without creating an instance.
    
    Args:
        video_path: Path to the video file
        audio_path: Path to the audio file
        subtitle_path: Path to the SRT subtitle file (optional)
        script_data: Dictionary containing script metadata (optional)
        output_dir: Directory where assembled videos will be saved
        output_filename: Name for the output file (optional)
        
    Returns:
        Path to the assembled video file
    """
    assembler = VideoAssembler(output_dir=output_dir)
    return assembler.assemble(
        video_path=video_path,
        audio_path=audio_path,
        subtitle_path=subtitle_path,
        script_data=script_data,
        output_filename=output_filename
    )


if __name__ == "__main__":
    # Example usage
    import argparse

    script = {
        "title": "Breaking the Matrix of Credentialism",
        "hook": "Morpheus was right: the rules were illusions.",
        "narration": "Schools taught us degrees = success. AI proves otherwise. The Matrix wasn\u2019t just a movie\u2014it\u2019s our mental prison of \u2018you can\u2019t do X without Y.\u2019 High-agency people hack the system. They see credentials as speed bumps, not requirements. Like Neo realizing he could dodge bullets, founders now bypass traditional gatekeepers. The hardest part? Believing you\u2019re allowed to jump. AI\u2019s the red pill\u2014swallow it, and watch the old world dissolve.",
        "cta": "Unplug from the system. Build anyway.",
        "keywords": [
          "#mindset",
          "#disruption",
          "#AIfuture"
        ],
        "estimated_duration_sec": 52
    }
    assembler = VideoAssembler(output_dir="my_videos")

    # Assemble the video
    output_path = assembler.assemble(
        video_path="/Users/mori/Desktop/tech_projects/liminal-ai/output/video/credit.mp4",
        audio_path="/Users/mori/Desktop/tech_projects/liminal-ai/output/audio/credit.mp3",
        subtitle_path="/Users/mori/Desktop/tech_projects/liminal-ai/output/audio/credit.srt",
        output_filename="final_video.mp4"
    )

print(f"Video saved to: {output_path}")
