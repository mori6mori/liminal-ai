"""
orchestrator.py - Orchestrates the full content-to-video pipeline

This module coordinates the entire pipeline process:
1. Chunking - Create a script from the content
3. Voiceover (TTS) - Generate audio narration
4. B-Roll Generation - Create visual content
5. Video Assembly - Combine all elements into final video
"""

import os
import json
import time
from typing import List, Dict, Any, Union

from chunker import ScriptGenerator
from tts import TextToSpeech
# from broll import BRollGenerator
# from assembler import VideoAssembler
from caption_overlay import CaptionOverlay

def process(input_text: str):
    script_generator = ScriptGenerator()
    chunks = script_generator.generate_scripts(article_text=input_text)
    tts = TextToSpeech()

    print(f"{len(chunks)} scripts generated")

    for chunk in chunks:
        # Ensure chunk is a dictionary
        if not isinstance(chunk, dict):
            print(f"Warning: Skipping invalid chunk format: {type(chunk)}")
            continue
            
        # Check if this is a container with nested scripts in "structure"
        if "structure" in chunk and isinstance(chunk["structure"], list):
            print(f"Found nested structure with {len(chunk['structure'])} scripts")
         
            # Process each script in the structure
            for script in chunk["structure"]:
                print(script)
                if isinstance(script, dict):
                    print(f"Processing nested script: {script.get('title', 'Untitled')}")
                    voiceover = tts.generate_voiceover(script)
                    print(voiceover)
        else:
            # Process as a single script
            print(f"Processing script: {chunk.get('title', 'Untitled')}")
            voiceover = tts.generate_voiceover(chunk)
            print(voiceover)

        # After generating the video
        if "full_audio" in voiceover and os.path.exists(voiceover["full_audio"]):
            # Generate captions
            srt_file = tts.generate_caption(voiceover["full_audio"])
            
            # Add captions to video
            caption_overlay = CaptionOverlay()
            captioned_video = caption_overlay.add_captions_to_video(
                video_path=video_file,  # Path to the generated video
                srt_path=srt_file
            )
            
            print(f"Video with captions saved to: {captioned_video}")

if __name__ == "__main__":
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
    
   
    
    process(article_text)