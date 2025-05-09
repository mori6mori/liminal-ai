"""
test_pipeline.py - Test script for the content-to-video pipeline

This script contains a hard-coded text sample to test the pipeline functionality
without requiring external input.
"""

import os
import sys
from orchestrator import process

# Add the pipeline directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Hard-coded test content
TEST_CONTENT = """
# The Future of Artificial Intelligence

Artificial intelligence (AI) is transforming our world in unprecedented ways. From healthcare to transportation, education to entertainment, AI technologies are revolutionizing how we live and work.

## Machine Learning Advancements

Recent breakthroughs in machine learning, particularly deep learning, have enabled computers to recognize patterns, understand language, and make decisions with increasing accuracy. Neural networks with billions of parameters can now generate human-like text, create realistic images, and solve complex problems.

## Ethical Considerations

As AI becomes more powerful, important ethical questions arise. How do we ensure AI systems are fair and unbiased? Who is responsible when AI makes mistakes? How can we protect privacy in an age of intelligent surveillance? These questions require thoughtful consideration from technologists, policymakers, and society at large.

## The Road Ahead

The future of AI holds immense promise. We may see AI assistants that truly understand our needs, medical AI that diagnoses diseases earlier than human doctors, and AI systems that help solve global challenges like climate change. However, realizing this potential requires responsible development and deployment of these powerful technologies.
"""

def run_test():
    """
    Run the pipeline with the test content
    """
    print("=" * 80)
    print("TESTING CONTENT-TO-VIDEO PIPELINE")
    print("=" * 80)
    print("\nTest content:")
    print("-" * 40)
    print(TEST_CONTENT[:300] + "...")  # Print just the beginning
    print("-" * 40)
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process the test content
    try:
        videos = process(TEST_CONTENT, output_dir=output_dir)
        
        if videos:
            print("\n✅ Test completed successfully!")
            print(f"Generated {len(videos)} videos:")
            for i, video in enumerate(videos):
                print(f"  {i+1}. {os.path.basename(video)}")
        else:
            print("\n❌ Test failed: No videos were generated")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test() 