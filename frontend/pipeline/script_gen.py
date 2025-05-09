"""
script_gen.py - Generates a TikTok-style script from content chunks

Input: Content chunks
Output: Script with segments for short-form video
"""

import openai
import os
import json
from typing import List, Dict, Any

class ScriptGenerator:
    def __init__(self, api_key=None, model="gpt-4"):
        """
        Initialize the script generator
        
        Args:
            api_key (str, optional): OpenAI API key
            model (str): Model to use for generation
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.model = model
    
    def generate_script(self, chunks: List[str], target_duration=60, style="informative") -> Dict[str, Any]:
        """
        Generate a script from content chunks
        
        Args:
            chunks (list): List of content chunks
            target_duration (int): Target duration in seconds
            style (str): Style of the script (informative, entertaining, etc.)
            
        Returns:
            dict: Script with segments
        """
        # Combine chunks into a summary for context
        combined_text = " ".join(chunks)
        
        # Create system prompt based on style and target duration
        system_prompt = self._create_system_prompt(style, target_duration)
        
        try:
            # Generate script using OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": combined_text}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract and parse the script
            script_text = response.choices[0].message.content
            script = self._parse_script(script_text)
            
            return script
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return {"error": str(e)}
    
    def _create_system_prompt(self, style, target_duration):
        """
        Create a system prompt based on style and target duration
        
        Args:
            style (str): Style of the script
            target_duration (int): Target duration in seconds
            
        Returns:
            str: System prompt
        """
        prompts = {
            "informative": f"You are an expert at creating engaging, informative short-form video scripts. Create a script for a {target_duration}-second TikTok or Instagram Reels video that explains the main points from the provided content. The script should be clear, concise, and educational. Format your response as a JSON object with a 'title', 'summary', and 'segments' array. Each segment should have 'text' (what to say) and 'duration' (in seconds).",
            
            "entertaining": f"You are an expert at creating entertaining, viral short-form video scripts. Create a script for a {target_duration}-second TikTok or Instagram Reels video that presents the key points from the provided content in an entertaining way. Use humor, analogies, and a conversational tone. Format your response as a JSON object with a 'title', 'summary', and 'segments' array. Each segment should have 'text' (what to say) and 'duration' (in seconds).",
            
            "educational": f"You are an expert at creating educational short-form video scripts. Create a script for a {target_duration}-second TikTok or Instagram Reels video that teaches the main concepts from the provided content. The script should be structured like a mini-lesson with clear explanations. Format your response as a JSON object with a 'title', 'summary', and 'segments' array. Each segment should have 'text' (what to say) and 'duration' (in seconds)."
        }
        
        return prompts.get(style, prompts["informative"])
    
    def _parse_script(self, script_text):
        """
        Parse the script text into a structured format
        
        Args:
            script_text (str): Script text from the API
            
        Returns:
            dict: Structured script
        """
        try:
            # Try to parse as JSON
            script = json.loads(script_text)
            
            # Validate the structure
            if not all(key in script for key in ["title", "summary", "segments"]):
                raise ValueError("Script is missing required fields")
            
            # Ensure each segment has required fields
            for segment in script["segments"]:
                if not all(key in segment for key in ["text", "duration"]):
                    raise ValueError("Segment is missing required fields")
            
            return script
            
        except json.JSONDecodeError:
            # If not valid JSON, try to parse the text format
            return self._parse_text_format(script_text)
    
    def _parse_text_format(self, script_text):
        """
        Parse non-JSON formatted script text
        
        Args:
            script_text (str): Script text
            
        Returns:
            dict: Structured script
        """
        lines = script_text.strip().split("\n")
        title = ""
        summary = ""
        segments = []
        
        # Simple parsing logic - can be improved
        for line in lines:
            line = line.strip()
            if line.startswith("Title:"):
                title = line[6:].strip()
            elif line.startswith("Summary:"):
                summary = line[8:].strip()
            elif ":" in line and not line.startswith(("Title:", "Summary:")):
                # Assume it's a segment
                parts = line.split(":", 1)
                if len(parts) == 2:
                    text = parts[1].strip()
                    # Estimate duration based on word count (3 words per second)
                    word_count = len(text.split())
                    duration = max(1, round(word_count / 3))
                    segments.append({"text": text, "duration": duration})
        
        return {
            "title": title,
            "summary": summary,
            "segments": segments
        }


if __name__ == "__main__":
    # Example usage
    # Make sure to set OPENAI_API_KEY environment variable or pass it to the constructor
    # generator = ScriptGenerator()
    
    # Sample chunks
    # chunks = [
    #     "Climate change is the long-term alteration of temperature and typical weather patterns in a place.",
    #     "The cause of current climate change is largely human activity, like burning fossil fuels, which adds greenhouse gases to the atmosphere."
    # ]
    
    # Generate script
    # script = generator.generate_script(chunks)
    # print(json.dumps(script, indent=2)) 