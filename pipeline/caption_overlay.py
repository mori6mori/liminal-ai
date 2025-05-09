"""
caption_overlay.py - Adds captions to videos using SRT files

This module takes a video file and an SRT file and creates a new video with captions.
"""

import os
import srt
import datetime
from typing import List, Dict, Any
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from dotenv import load_dotenv

load_dotenv()

class CaptionOverlay:
    def __init__(self, output_dir="output/video"):
        """
        Initialize the caption overlay module
        
        Args:
            output_dir (str): Directory to save output videos
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def add_captions_to_video(self, video_path: str, srt_path: str, output_path: str = None) -> str:
        """
        Add captions from an SRT file to a video
        
        Args:
            video_path (str): Path to the input video file
            srt_path (str): Path to the SRT file containing captions
            output_path (str, optional): Path to save the output video
            
        Returns:
            str: Path to the output video with captions
        """
        # Generate output path if not provided
        if not output_path:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}_captioned.mp4")
        
        # Load the video
        video = VideoFileClip(video_path)
        
        # Parse the SRT file
        with open(srt_path, 'r') as f:
            srt_content = f.read()
            subtitles = list(srt.parse(srt_content))
        
        # Create text clips for each subtitle
        text_clips = []
        for subtitle in subtitles:
            # Convert subtitle times to seconds
            start_time = subtitle.start.total_seconds()
            end_time = subtitle.end.total_seconds()
            
            # Create text clip
            txt_clip = TextClip(
                subtitle.content, 
                fontsize=24, 
                color='white',
                bg_color='black',
                stroke_color='black',
                stroke_width=1,
                method='caption',
                align='center',
                size=(video.w * 0.8, None)  # Width is 80% of video width
            )
            
            # Position at the bottom of the frame with some padding
            txt_clip = txt_clip.set_position(('center', video.h - 80))
            
            # Set the duration
            txt_clip = txt_clip.set_start(start_time).set_end(end_time)
            
            text_clips.append(txt_clip)
        
        # Overlay the text clips on the video
        final_video = CompositeVideoClip([video] + text_clips)
        
        # Write the result to a file
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Close the clips to free resources
        video.close()
        final_video.close()
        
        return output_path
    
    def batch_process(self, video_dir: str, srt_dir: str) -> List[str]:
        """
        Process all videos in a directory, adding captions from matching SRT files
        
        Args:
            video_dir (str): Directory containing video files
            srt_dir (str): Directory containing SRT files
            
        Returns:
            List[str]: Paths to all processed videos
        """
        processed_videos = []
        
        # Get all video files
        video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.mov', '.avi'))]
        
        for video_file in video_files:
            base_name = os.path.splitext(video_file)[0]
            srt_file = f"{base_name}.srt"
            srt_path = os.path.join(srt_dir, srt_file)
            
            # Check if matching SRT file exists
            if os.path.exists(srt_path):
                video_path = os.path.join(video_dir, video_file)
                output_path = os.path.join(self.output_dir, f"{base_name}_captioned.mp4")
                
                try:
                    processed_video = self.add_captions_to_video(video_path, srt_path, output_path)
                    processed_videos.append(processed_video)
                    print(f"Added captions to {video_file}")
                except Exception as e:
                    print(f"Error processing {video_file}: {str(e)}")
            else:
                print(f"No matching SRT file found for {video_file}")
        
        return processed_videos


if __name__ == "__main__":
    # Example usage
    caption_overlay = CaptionOverlay()
    
    # Process a single video
    video_path = "output/video/sample_video.mp4"
    srt_path = "output/audio/sample_audio.srt"
    
    if os.path.exists(video_path) and os.path.exists(srt_path):
        output_path = caption_overlay.add_captions_to_video(video_path, srt_path)
        print(f"Video with captions saved to: {output_path}")
    else:
        print("Sample files not found. Please provide valid video and SRT paths.") 