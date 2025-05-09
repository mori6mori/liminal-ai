"""
orchestrator.py - Orchestrates the full content-to-video pipeline

This module coordinates the entire pipeline process:
1. Chunking - Break down longform content into manageable chunks
2. Script Generation - Create a script from the content
3. Voiceover (TTS) - Generate audio narration
4. B-Roll Generation - Create visual content
5. Video Assembly - Combine all elements into final video
"""

import os
import json
import time
from typing import List, Dict, Any, Union

from chunker import Chunker
from script_gen import ScriptGenerator
from tts import TextToSpeech
from broll import BRollGenerator
from assembler import VideoAssembler

def process(text: str, output_dir: str = "output", voice_id: str = "Rachel") -> List[str]:
    """
    Process text through the entire content-to-video pipeline
    
    Args:
        text (str): Input text content
        output_dir (str): Directory to store output files
        voice_id (str): Voice ID for TTS
        
    Returns:
        list: List of generated video file paths
    """
    print("🚀 Starting content-to-video pipeline")
    start_time = time.time()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    chunker = Chunker(max_chunk_size=1000, overlap=100)
    script_generator = ScriptGenerator()
    tts_engine = TextToSpeech(voice=voice_id)
    broll_generator = BRollGenerator()
    video_assembler = VideoAssembler()
    
    # Step 1: Chunk the content
    print("📄 Chunking content...")
    chunks = chunker.chunk_text(text)
    print(f"   Created {len(chunks)} chunks")
    
    generated_videos = []
    
    # Process each chunk
    for i, chunk in enumerate(chunks):
        chunk_start_time = time.time()
        print(f"\n🔄 Processing chunk {i+1}/{len(chunks)}")
        
        try:
            # Step 2: Generate script
            print(f"📝 Generating script for chunk {i+1}...")
            script = script_generator.generate_script([chunk])
            
            # Step 3: Generate voiceover
            print(f"🎙️ Creating voiceover for chunk {i+1}...")
            voiceover = tts_engine.generate_voiceover(script)
            
            # Step 4: Generate B-Roll
            print(f"🎬 Generating B-Roll for chunk {i+1}...")
            broll = broll_generator.generate_broll(script)
            
            # Step 5: Assemble video
            print(f"🎥 Assembling video for chunk {i+1}...")
            video = video_assembler.assemble_video(script, voiceover, broll)
            
            if "error" not in video:
                generated_videos.append(video["video_file"])
                print(f"✅ Generated video {i+1}: {video['video_file']}")
                print(f"   Duration: {voiceover['duration']:.2f} seconds")
                print(f"   Processing time: {time.time() - chunk_start_time:.2f} seconds")
            else:
                print(f"❌ Failed to generate video for chunk {i+1}: {video.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing chunk {i+1}: {str(e)}")
    
    # Final report
    total_time = time.time() - start_time
    print(f"\n✨ Pipeline complete!")
    print(f"   Total videos generated: {len(generated_videos)}/{len(chunks)}")
    print(f"   Total processing time: {total_time:.2f} seconds")
    
    return generated_videos

def process_file(file_path: str, output_dir: str = "output", voice_id: str = "Rachel") -> List[str]:
    """
    Process a file through the content-to-video pipeline
    
    Args:
        file_path (str): Path to the input file
        output_dir (str): Directory to store output files
        voice_id (str): Voice ID for TTS
        
    Returns:
        list: List of generated video file paths
    """
    print(f"📂 Processing file: {file_path}")
    
    # Initialize chunker
    chunker = Chunker()
    
    # Extract content from file
    chunks = chunker.process_file(file_path)
    
    if not chunks:
        print("❌ Failed to extract content from file")
        return []
    
    # Process the extracted content
    return process(" ".join(chunks), output_dir, voice_id)

def process_url(url: str, output_dir: str = "output", voice_id: str = "Rachel") -> List[str]:
    """
    Process a URL through the content-to-video pipeline
    
    Args:
        url (str): URL to process
        output_dir (str): Directory to store output files
        voice_id (str): Voice ID for TTS
        
    Returns:
        list: List of generated video file paths
    """
    print(f"🌐 Processing URL: {url}")
    
    # Initialize chunker
    chunker = Chunker()
    
    # Extract content from URL
    chunks = chunker.process_url(url)
    
    if not chunks:
        print("❌ Failed to extract content from URL")
        return []
    
    # Process the extracted content
    return process(" ".join(chunks), output_dir, voice_id)

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py [text|file|url] [input] [output_dir] [voice_id]")
        sys.exit(1)
    
    input_type = sys.argv[1]
    input_value = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    voice_id = sys.argv[4] if len(sys.argv) > 4 else "Rachel"
    
    if input_type == "text":
        videos = process(input_value, output_dir, voice_id)
    elif input_type == "file":
        videos = process_file(input_value, output_dir, voice_id)
    elif input_type == "url":
        videos = process_url(input_value, output_dir, voice_id)
    else:
        print(f"Unknown input type: {input_type}")
        sys.exit(1)
    
    print(f"\nGenerated videos: {videos}") 