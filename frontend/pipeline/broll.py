"""
broll.py - Generates B-Roll footage based on script content

Input: Script with segments
Output: B-Roll video clips
"""

import os
import json
import requests
import tempfile
from typing import Dict, List, Any
import cv2
import numpy as np
from PIL import Image
import time

class BRollGenerator:
    def __init__(self, api_key=None):
        """
        Initialize the B-Roll generator
        
        Args:
            api_key (str, optional): API key for image/video generation
        """
        self.api_key = api_key or os.environ.get("BROLL_API_KEY")
        self.output_dir = "output/broll"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_broll(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate B-Roll for the entire script
        
        Args:
            script (dict): Script with segments
            
        Returns:
            dict: B-Roll data with video file paths
        """
        try:
            segments = script.get("segments", [])
            broll_clips = []
            
            for i, segment in enumerate(segments):
                # Extract keywords from the segment text
                keywords = self._extract_keywords(segment["text"])
                
                # Generate B-Roll for this segment
                clip_file = self._generate_segment_broll(keywords, segment["text"], f"segment_{i}")
                
                # Add to list of clips
                broll_clips.append({
                    "id": i,
                    "text": segment["text"],
                    "keywords": keywords,
                    "video_file": clip_file
                })
            
            return {
                "title": script.get("title", ""),
                "clips": broll_clips
            }
            
        except Exception as e:
            print(f"Error generating B-Roll: {e}")
            return {"error": str(e)}
    
    def _extract_keywords(self, text):
        """
        Extract keywords from text for B-Roll generation
        
        Args:
            text (str): Text to extract keywords from
            
        Returns:
            list: List of keywords
        """
        # This is a simple implementation - in a real system, you might use NLP
        # to extract more meaningful keywords
        
        # Remove common words and punctuation
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "about", "like", "through", "over", "before", "after", "since", "during", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "of", "from", "as"}
        
        words = text.lower().split()
        words = [word.strip(".,!?;:()[]{}\"'") for word in words]
        keywords = [word for word in words if word and word not in common_words and len(word) > 3]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _generate_segment_broll(self, keywords, text, segment_id):
        """
        Generate B-Roll for a single segment
        
        Args:
            keywords (list): Keywords extracted from the segment
            text (str): Full text of the segment
            segment_id (str): Identifier for the segment
            
        Returns:
            str: Path to the generated video file
        """
        # This is a placeholder for the actual B-Roll generation
        # In a real implementation, you would call your image/video generation service
        
        if self.api_key and keywords:
            # Example using a hypothetical image generation API
            try:
                # Use the first few keywords to generate an image
                prompt = " ".join(keywords[:3])
                response = self._call_image_api(prompt)
                
                # Save the image
                image_file = os.path.join(self.output_dir, f"{segment_id}_image.jpg")
                with open(image_file, "wb") as f:
                    f.write(response.content)
                
                # Convert image to video clip
                video_file = self._image_to_video(image_file, segment_id)
                return video_file
                
            except Exception as e:
                print(f"Error calling image API: {e}")
                # Fall back to the mock implementation
                return self._mock_broll(segment_id)
        else:
            # Use mock implementation for testing
            return self._mock_broll(segment_id)
    
    def _call_image_api(self, prompt):
        """
        Call the image generation API
        
        Args:
            prompt (str): Text prompt for image generation
            
        Returns:
            Response: API response
        """
        # This is a placeholder - replace with your actual image generation API
        url = "https://api.example.com/generate-image"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "size": "1080x1920",  # Vertical video format
            "format": "jpg"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response
    
    def _image_to_video(self, image_path, segment_id, duration=5):
        """
        Convert a still image to a video clip
        
        Args:
            image_path (str): Path to the image
            segment_id (str): Identifier for the segment
            duration (int): Duration of the clip in seconds
            
        Returns:
            str: Path to the generated video file
        """
        # Load the image
        img = cv2.imread(image_path)
        
        # Resize to vertical video format (1080x1920)
        img = cv2.resize(img, (1080, 1920))
        
        # Create a video writer
        output_file = os.path.join(self.output_dir, f"{segment_id}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        video = cv2.VideoWriter(output_file, fourcc, fps, (1080, 1920))
        
        # Write the image to the video for the specified duration
        for _ in range(duration * fps):
            video.write(img)
        
        # Release the video writer
        video.release()
        
        return output_file
    
    def _mock_broll(self, segment_id, duration=5):
        """
        Create a mock B-Roll video for testing
        
        Args:
            segment_id (str): Identifier for the segment
            duration (int): Duration of the clip in seconds
            
        Returns:
            str: Path to the generated video file
        """
        # Create a blank image
        width, height = 1080, 1920  # Vertical video format
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f"B-Roll {segment_id}", (width//4, height//2), font, 2, (255, 255, 255), 3)
        
        # Create a video writer
        output_file = os.path.join(self.output_dir, f"{segment_id}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 30
        video = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
        # Write the image to the video for the specified duration
        for _ in range(duration * fps):
            video.write(img)
        
        # Release the video writer
        video.release()
        
        return output_file


if __name__ == "__main__":
    # Example usage
    # generator = BRollGenerator()
    
    # Sample script
    # script = {
    #     "title": "Climate Change Explained",
    #     "segments": [
    #         {"text": "Climate change is affecting our planet in unprecedented ways.", "duration": 5},
    #         {"text": "Human activities are the main driver of these changes.", "duration": 4}
    #     ]
    # }
    
    # Generate B-Roll
    # broll = generator.generate_broll(script)
    # print(json.dumps(broll, indent=2)) 