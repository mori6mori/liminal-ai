# Liminal.ai

A content-to-video conversion pipeline that transforms longform text or PDFs into short-form videos.

## Overview

This project transforms longform text content into engaging short-form videos through a series of AI-powered steps:

1. **Content Chunking**: Breaks down articles into script segments optimized for short videos
2. **Text-to-Speech**: Converts scripts into natural-sounding voiceovers
3. **B-Roll Generation**: Creates relevant visual content to accompany the narration
4. **Video Assembly**: Combines all elements into the final video

## Pipeline Components

- **Chunker**: Breaks down longform content into manageable chunks
- **Script Generator**: Creates a script from content chunks
- **TTS Engine**: Generates voiceover audio from the script
- **B-Roll Generator**: Creates visual content based on the script
- **Video Assembler**: Combines audio and visuals into the final video
- **Orchestrator**: Coordinates the entire pipeline process

## Features

- Process articles, blog posts, or any longform text
- Generate engaging scripts with hooks and calls-to-action
- Create natural-sounding voiceovers using ElevenLabs
- Automatically assemble complete videos ready for social media

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/liminal-ai.git
cd liminal-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with your API keys:

```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_preferred_voice_id
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## Usage

```python
from pipeline.orchestrator import process

# Process an article
article_text = """
Your article text goes here...
"""

process(article_text)
```

## Project Structure

```
liminal-ai/
├── pipeline/
│   ├── __init__.py
│   ├── chunker.py
│   ├── tts.py
│   ├── broll.py (coming soon)
│   ├── assembler.py (coming soon)
│   └── orchestrator.py
├── output/
│   ├── audio/
│   ├── video/
│   └── scripts/
├── .env
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- ElevenLabs API key
- DeepSeek API key
- FFmpeg (for video processing)
- pydub
- requests
- python-dotenv
- beautifulsoup4
- nltk

## Setup and Usage

[Instructions here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.