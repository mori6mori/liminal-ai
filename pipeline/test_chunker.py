import unittest
import sys
import os
from io import StringIO
from openai import OpenAI

# Add the parent directory to the path so we can import the chunker module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.chunker import Chunker

class TestChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = Chunker(max_chunk_size=500, overlap=50)
        
        # Sample text for testing
        self.sample_text = """
        Artificial Intelligence in Scientific Research
        
        Introduction
        Artificial Intelligence (AI) has emerged as a transformative force in scientific research, 
        revolutionizing how scientists approach complex problems and analyze vast datasets. 
        Machine learning algorithms can now identify patterns that would take humans years to discover.
        
        Applications
        In genomics, AI tools rapidly sequence and analyze DNA, accelerating discoveries in medicine.
        Astronomy uses neural networks to classify galaxies and detect exoplanets from telescope data.
        Climate scientists employ AI to improve weather predictions and model complex climate systems.
        
        Challenges
        Despite its promise, AI integration faces obstacles including data quality issues, 
        interpretability problems, and the need for specialized expertise. 
        Ethical considerations around bias and transparency remain significant concerns.
        
        Future Directions
        The next frontier involves developing more explainable AI systems and 
        creating hybrid approaches that combine human expertise with machine capabilities.
        """
    
    def test_clean_text(self):
        """Test the text cleaning functionality"""
        cleaned_text = self.chunker._clean_text(self.sample_text)
        self.assertFalse("\n\n" in cleaned_text)
        self.assertFalse("  " in cleaned_text)
        self.assertTrue(cleaned_text.startswith("Artificial Intelligence"))
    
    def test_chunk_text(self):
        """Test the text chunking functionality"""
        chunks = self.chunker.chunk_text(self.sample_text)
        self.assertGreater(len(chunks), 0)
        # Check that no chunk exceeds the max size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), self.chunker.max_chunk_size)
    
    def test_prepare_for_script_generation(self):
        """Test the prompt preparation functionality"""
        prompt_messages = self.chunker.prepare_for_script_generation(self.sample_text)
        
        # Check that we have the expected message structure
        self.assertEqual(len(prompt_messages), 2)
        self.assertEqual(prompt_messages[0]["role"], "system")
        self.assertEqual(prompt_messages[1]["role"], "user")
        
        # Check that the user message contains our sample text
        self.assertIn("Artificial Intelligence in Scientific Research", prompt_messages[1]["content"])
    
    def test_build_prompt(self):
        """Test the prompt building functionality"""
        prompt = self.chunker.build_prompt("Test article")
        self.assertEqual(len(prompt), 2)
        self.assertEqual(prompt[0]["role"], "system")
        self.assertEqual(prompt[1]["role"], "user")
        self.assertIn("Test article", prompt[1]["content"])
        
    def test_process_content_text(self):
        """Test processing direct text input"""
        processed = self.chunker.process_content(self.sample_text, content_type="text")
        self.assertIsInstance(processed, str)
        self.assertGreater(len(processed), 0)

    def test_full_workflow_with_output(self):
        """Test the full workflow and print the results"""
        print("\n--- Testing full workflow with sample text ---")
        
        # Process the sample text
        processed_text = self.chunker.process_content(self.sample_text)
        print(f"\nProcessed text:")
        print(processed_text)
        
        # Chunk the text
        chunks = self.chunker.chunk_text(self.sample_text)
        print(f"\nGenerated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1} (length {len(chunk)}):")
            print(chunk)
        
        # Generate prompt
        prompt = self.chunker.prepare_for_script_generation(self.sample_text)
        print(f"\nGenerated prompt with {len(prompt)} messages:")
        for msg in prompt:
            print(f"\n{msg['role'].upper()} MESSAGE:")
            print(msg['content'])
        
        # Verify outputs
        self.assertIsInstance(processed_text, str)
        self.assertGreater(len(processed_text), 0)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(len(prompt), 2)

if __name__ == "__main__":
    unittest.main()
    print("Running chunker tests...")
    unittest.main()