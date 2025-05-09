"""
chunker.py - Breaks down longform content into manageable chunks and prepares content for script generation

Input: Longform text, PDF content, URLs, or direct text content
Output: Processed content ready for script generation
"""

import re
import json
import textwrap
import PyPDF2
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from typing import List, Dict, Optional

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now access the environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

class ScriptGenerator:
    def __init__(self, api_key=DEEPSEEK_API_KEY, model="deepseek-chat"):
        """Initialize the script generator with API key and model.
        
        Args:
            api_key: The API key for DeepSeek or OpenAI
            model: The model to use (default: "deepseek-chat")
        """
        self.api_key = api_key
        self.model = model
        self.is_deepseek = "deepseek" in model.lower()
        
        # Use the appropriate client based on the model
        if self.is_deepseek:
            # For DeepSeek, we'll use requests directly since there's no official Python client
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
        else:
            # For OpenAI models
            self.client = OpenAI(api_key=api_key)
        
        self.SYSTEM_MSG = (
            "You are an expert explainer who turns dense academic papers into short, "
            "high‑engagement vertical‑video scripts for Gen‑Z."
        )
        self.USER_TEMPLATE = textwrap.dedent("""
            Your task has two stages:

            **Stage A – Section map**
            Read the article text (between ```...```). Identify its 3-6 major conceptual sections.
            Return them as an ordered JSON array called "structure".

            **Stage B – Video transcripts** 
            For each section you found:
            - Compress it into an ~100-130 word script for a 35-60s video
            - Hook the viewer in the first line, use clear metaphors, avoid jargon, second-person voice
            - End with either a teaser or a punchy takeaway

            Return a JSON object with the following fields:
            - title: A catchy, SEO-friendly title (max 100 chars)
            - hook: An attention-grabbing opening line (15-20 words) 
            - narration: The main script content (100-130 words)
            - cta: A call-to-action or key takeaway (10-15 words)
            - keywords: 3-5 relevant keywords or hashtags
            - estimated_duration_sec: Estimated duration in seconds (35-60)

            Format the response as a single line of minified JSON.

            ARTICLE
            ```
            {article_text}
            ```
        """)

    def generate_scripts(self, article_text: str) -> List[Dict]:
        """Generate scripts from article text.
        
        Args:
            article_text: The article text to process
            
        Returns:
            List of script dictionaries
        """
        prompt = self.USER_TEMPLATE.format(article_text=article_text)
        
        # Create API call parameters
        messages = [
            {"role": "system", "content": self.SYSTEM_MSG},
            {"role": "user", "content": prompt}
        ]
        
        # Make the API call based on the model type
        try:
            if self.is_deepseek:
                # Use requests for DeepSeek API
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                response = requests.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()  # Raise exception for HTTP errors
                result = response.json()
                content = result["choices"][0]["message"]["content"]
            else:
                # Use OpenAI client for OpenAI models
                params = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                response = self.client.chat.completions.create(**params)
                content = response.choices[0].message.content
        except Exception as e:
            print(f"API call failed: {str(e)}")
            raise
            
        # Clean the content - handle markdown code blocks
        if "```json" in content:
            # Extract JSON from markdown code block
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            # Extract content from any code block
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            scripts = json.loads(content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {content}")
            # Try one more approach - sometimes there's an outer JSON structure
            try:
                # Look for a JSON object within the string
                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    scripts = json.loads(json_match.group(1))
                else:
                    raise ValueError(f"Response could not be parsed as JSON:\n{content}")
            except:
                raise ValueError(f"Response could not be parsed as JSON:\n{content}")

        # Ensure we return a list of dictionaries
        result = []
        
        # If the response is a dict with multiple sections
        if isinstance(scripts, dict):
            if "transcripts" in scripts:
                # If it has a "transcripts" key, use that list
                transcripts = scripts["transcripts"]
                if isinstance(transcripts, list):
                    result = transcripts
                else:
                    result = [transcripts]
            elif "title" in scripts and "narration" in scripts:
                # If it's a single script, return it as a list with one item
                result = [scripts]
            else:
                # Extract any dictionary values
                for k, v in scripts.items():
                    if isinstance(v, dict):
                        result.append(v)
                if not result:
                    # If no dictionaries found, use the whole dict
                    result = [scripts]
        elif isinstance(scripts, list):
            # If it's already a list, ensure each item is a dictionary
            for item in scripts:
                if isinstance(item, dict):
                    result.append(item)
                else:
                    print(f"Skipping non-dictionary item in list: {item}")
        else:
            raise ValueError(f"Unexpected JSON format in response: {type(scripts)}")
        
        # Final check - ensure we have at least one dictionary
        if not result:
            raise ValueError("No valid script dictionaries found in response")
            
        print(f"Returning {len(result)} script(s)")
        return result


class Chunker:
    def __init__(self, max_chunk_size=1000, overlap=100):
        """Initialize the chunker with configuration."""
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
    def process_content(self, content, content_type="text"):
        """Process content based on its type."""
        if content_type == "text":
            # Direct text input
            return self._clean_text(content)
        elif content_type == "file":
            # File path
            return self.process_file(content)
        elif content_type == "url":
            # URL
            return self.process_url(content)
        elif content_type == "binary":
            # Binary data (e.g., PDF)
            if isinstance(content, bytes):
                return self._extract_pdf_content(BytesIO(content))
            else:
                raise ValueError("Binary content must be bytes")
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
    
    def _clean_text(self, text):
        """Clean text by removing extra whitespace, etc."""
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def chunk_text(self, text):
        """Split text into semantically meaningful chunks."""
        # Clean the text
        text = self._clean_text(text)
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max size, start a new chunk
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from previous chunk
                overlap_point = max(0, len(current_chunk) - self.overlap)
                current_chunk = current_chunk[overlap_point:] + sentence + " "
            else:
                current_chunk += sentence + " "
        
        # Add the last chunk if it's not empty
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def build_prompt(self, article_text: str) -> List[Dict[str, str]]:
        """Build a prompt for the LLM based on the article text."""
        system_msg = (
            "You are an expert explainer who turns dense academic papers into short, "
            "high‑engagement vertical‑video scripts for Gen‑Z."
        )
        
        user_template = textwrap.dedent("""
            Your task has two stages:

            **Stage A – Section map**
            Read the article text (between ```...```). Identify its 3-6 major conceptual sections.
            Return them as an ordered JSON array called "structure".

            **Stage B – Video transcripts** 
            For each section you found:
            - Compress it into an ~100-130 word script for a 35-60s video
            - Hook the viewer in the first line, use clear metaphors, avoid jargon, second-person voice
            - End with either a teaser or a punchy takeaway

            Return a JSON object with the following fields:
            - title: A catchy, SEO-friendly title (max 100 chars)
            - hook: An attention-grabbing opening line (15-20 words) 
            - narration: The main script content (100-130 words)
            - cta: A call-to-action or key takeaway (10-15 words)
            - keywords: 3-5 relevant keywords or hashtags
            - estimated_duration_sec: Estimated duration in seconds (35-60)

            Format the response as a single line of minified JSON.

            ARTICLE
            ```
            {article_text}
            ```
            """)
        
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_template.format(article_text=article_text)},
        ]
    
    def prepare_for_script_generation(self, content, content_type="text") -> List[Dict[str, str]]:
        """Prepare content for script generation."""
        # Process the content based on its type
        processed_content = self.process_content(content, content_type)
        
        # Build the prompt
        return self.build_prompt(processed_content)


if __name__ == "__main__":
    # Test the ScriptGenerator class
    print("Initializing ScriptGenerator with DeepSeek API...")
    script_generator = ScriptGenerator(api_key=DEEPSEEK_API_KEY)
    
    # Example usage
    article_text = """
    Agency is Eating the World
    April 2025

    This essay has been featured on Pirate Wires. -- In 2023, Sam Altman famously said, "There'll soon be a 1-person billion-dollar company." Two years later, we're watching his prediction unfold — not simply because of AI, but because of the kind of individuals who are wielding it. A new breed of companies is emerging: lean, unconventional, and wildly successful. They generate hundreds of millions of dollars and yet have no sales teams, no marketing departments, no formal HR, not even vertically specialized engineers. They're led by a handful of people doing the work of hundreds, leveraging machines to scale their impact.

    For years, we feared automation would replace humans. But as AI reshapes the economy, it's becoming clear that far from replacing human ingenuity, AI has amplified it. The critical dividing line in our economy is no longer simply education or specialization, but rather agency itself: the raw determination to make things happen without waiting for permission.

    Agency
    The word agency is thrown around a lot, these days. It's not always clear what it means. Many people in tech today, myself included, are working to create digital systems capable of interacting with and adapting to the external environment, to achieve specific outcomes. We call these programs "agents." A legal agent might autonomously scan court documents and compile a legal strategy; a financial agent might continuously monitor market conditions and dynamically adjust pricing or investment strategies.

    For the past three years, I've been part of the core team behind Replit, a coding agent that writes, runs, and deploys software programs autonomously. Despite its status as standard industry nomenclature1, I've grown to dislike the term "agent." I find it inaccurate. When building agents, we're giving programs everything except agency. The appeal of these tools lies in their combination of capability, maneuverability, and predictable behavior — they execute complex tasks while remaining fundamentally responsive to instructions.

    When, some time ago, a few companies started offering more independent coding models, customers didn't like them. The most successful AI products today are reactive, not proactive, and don't exhibit genuine independence, primarily because that's what customers want: programs that listen when told what to do. High-agency people don't.

    True agency is an unruly psychological trait. It's the willingness to act without explicit validation, instruction, or even permission. It's the meme "you can just do things," knowing that "you can poke life, and something will pop out the other side."2 It's a venture capitalist with no academic background founding the most important AI lab in history; a gaming entrepreneur creating a $30 billion military company; a fintech CEO birthing the private space industry out of thin air.

    True agency involves defiance, improvisation, instinct, and often irrationality. You don't need to be in tech to have high agency. Yet you'll find most of these people there, as they naturally gravitate toward low-structure, high-impact environments — namely, startups.

    While driven individuals capable of making things happen have always existed, their bandwidth has historically been limited. It's impossible to scale impact entirely alone. We live in a complex world: to accomplish anything significant, you still need specialization at some point, which takes time to acquire. You might want to "just do things," but that doesn't mean you have enough physical time to learn everything yourself.

    High-agency people aiming to achieve their goals still need to hire specialists or spend years selecting and mastering a discipline. When I founded my previous company a decade ago, it took me nine months to go from idea to working prototype — nine months spent essentially learning the basics required to build a digital product. And yet, this effort still didn't put me anywhere near the proficiency of a professional software developer, designer, or marketer.

    Becoming an expert takes time. Specialization is a necessary precondition for success, making it a form of local monopoly. We live in a homeostatic equilibrium: even the most intelligent and driven people can't possibly perform every job simultaneously. Stable ecological systems sustain themselves long-term precisely because the apex predator can't be everywhere at once.

    This dynamic explains why being more skilled and educated within a particular discipline confers a persistent advantage, and why on average our society favors credentials over outcomes. The optimal strategy is typically to follow the lead, stay in your lane, do your homework, and achieve top marks. To get a job, keep that job, specialize, and climb the ladder. There's a reason college tuition has outpaced inflation multiple times over. People hope it will help them develop specialized skills, creating their own form of vertical monopoly within the workforce.

    We don't live in a world that's kind to generalists. Well, until AI, that is.

    A phase shift
    We're now facing a rupture, a phase transition. AI has eroded the value of specialization because, for many tasks, achieving the outcome of several years of experience now takes a $20 ChatGPT subscription. If a decade ago it took me nine months to gain enough experience to ship a single prototype, now it takes just one week to build a state-of-the-art platform ready to be shipped — a project once only achievable by a full team of professionals.

    Skeptics will push back against this techno-optimism, arguing that AI is sloppy, intrinsically probabilistic and prone to mistakes. Build using AI, the story goes, and things will sure enough eventually break: you need an expert to know when to trust the machine. I understand, but disagree with the conclusion.

    While it's true that specialization hasn't become irrelevant, it no longer matters indiscriminately and uniformly anymore. I expect a bimodal-shaped distribution of AI deployment, depending on how comfortable we are — as a society — with risk. In industries where untrained people equipped with imperfect AI models could make costly mistakes, we are going to see demand for specialized human accountability.

    This will include sectors such as defense, healthcare, space exploration, biological research, and AI advancement itself — all domains where the variance of prediction models is higher than the acceptable risk threshold. Wherever mistakes can kill and AI can't prove to be virtually all-knowing, we can expect regulation to enforce natural barriers, and the need to hire experts. It's similar to why we continue to require human pilots despite having the technological capacity for autonomous flight. Sometimes, we just want the ability to point the finger.

    However, for most jobs this is not true. Wherever we are ok with "trying again" after getting a bad AI generation, we will see market disruption. Data science, marketing, financial modeling, education, graphic design, counseling, and architecture will all experience an influx of non-specialized, high-agency individuals.

    Sure, machines will keep making mistakes, but their rate of improvement has been astronomical, and will only continue to delay the point at which generalists feel the need to hire experts. Three years ago AI could simply auto-complete small code snippets. Two years ago it started fixing broken programs. Last year it began creating new projects from scratch. It now can autonomously understand large projects created by thousands of human developers, and be used even by non-professionals.

    The game has shifted, and the winning strategy with it. It's no longer about understanding specialized details; it's about grasping the high-level global picture. It's less about knowing how to patch a system and more about knowing that it needs to be patched. It's more about architecture, and less about implementation. Precisely where generalists thrive.

    For these individuals, boundaries between professions are beginning to blur and overlap. I've begun to see product managers developing business financial models; designers writing commercial ads; barbershops building custom booking systems; and restaurant owners creating advanced pricing tools. Even domains seemingly far from tech, like agriculture, are beginning to see this impact, with farmers building crop tracking systems. These people always had it in them to do these things. The key difference is that it no longer takes years to learn how.

    If you extend this argument to the limit, you end up with individuals running entire companies by themselves. The share of solo-founder startups has almost doubled in the last few years2, and the first examples of businesses with a handful of employees generating hundreds of millions of dollars in revenue have emerged.

    Henri Shi, who spent nearly a decade growing super.com into a $150M ARR business, is now tracking the progress towards Altman's one-person billion dollar company goal in a public leaderboard.4 He reports an average of $2.8 million in revenue per employee, coincidentally the same as Apple, the most valuable publicly traded US company of the past two decades. Companies like Midjourney, with its 40 employees and $500m of yearly revenues, represent a structural shift, not an anomaly.5 These companies are now full of high-agency individuals carrying the work of several teams, and are easily competing with much larger companies.

    This is the unraveling of credentialism. Having an edge in the market is no longer about knowing how to do something very specific very well; it's about being biased toward making it happen.

    A new world
    My entire world model has collapsed into a single bit: agency, or no agency. The transition will take time, and it will be far from painless. Institutions built around credentials won't go gently into the good night. Middle management will fight to keep headcount because it will take time to shift away from the idea that more people working on a problem signals a more important problem. Schools and colleges will take a while to adapt their teaching methods and content. Only bottom-up market competition will force change.

    Structure isn't always bad. One-person companies come with high chaos potential, and cascading errors can be hard to contain at scale. A solo operator lacks the redundancy of a team — when the AI fumbles, there's no safety net, and small mistakes like mishandled tax compliance can snowball into audits, bug fixes, social media rants, and refund chaos. Yet, these entrepreneurs will still prove to be mighty competitive forces that big firms can't ignore.

    The good news is that having high agency is an internal state of mind, and it can be absorbed. It means freeing oneself from artificial constraints and defying them. It's Morpheus challenging Neo in The Matrix: "Do you think that's air you're breathing now?" The limitations we've accepted as natural — degrees, credentials, specialized skills, years of experience — are no longer the barriers we believed they were to making things happen. Like Neo, the hardest part is simply believing we're free to jump.
    """
    
    print("Generating scripts...")
    try:
        scripts = script_generator.generate_scripts(article_text)
        print("Generated scripts:")
        print(json.dumps(scripts, indent=2))
    except Exception as e:
        print(f"Error generating scripts: {str(e)}")