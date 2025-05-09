"""
chunker.py - Breaks down longform content into manageable chunks

Input: Longform text or PDF content
Output: List of content chunks for further processing
"""

import re
import PyPDF2
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Chunker:
    def __init__(self, max_chunk_size=1000, overlap=100):
        """
        Initialize the chunker with configuration
        
        Args:
            max_chunk_size (int): Maximum size of each chunk in characters
            overlap (int): Overlap between chunks in characters
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def process_url(self, url):
        """
        Extract and chunk content from a URL
        
        Args:
            url (str): URL to extract content from
            
        Returns:
            list: List of content chunks
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Extract text based on content type
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                content = self._extract_pdf_content(BytesIO(response.content))
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                content = soup.get_text()
            
            # Clean and chunk the content
            return self.chunk_text(content)
            
        except Exception as e:
            print(f"Error processing URL: {e}")
            return []
    
    def process_file(self, file_path):
        """
        Extract and chunk content from a file
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            list: List of content chunks
        """
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    content = self._extract_pdf_content(file)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            
            # Clean and chunk the content
            return self.chunk_text(content)
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return []
    
    def _extract_pdf_content(self, file_obj):
        """
        Extract text content from a PDF file
        
        Args:
            file_obj: File object (can be BytesIO or file handle)
            
        Returns:
            str: Extracted text content
        """
        pdf_reader = PyPDF2.PdfReader(file_obj)
        content = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            content += page.extract_text() + "\n\n"
            
        return content
    
    def chunk_text(self, text):
        """
        Split text into semantically meaningful chunks
        
        Args:
            text (str): Text to chunk
            
        Returns:
            list: List of text chunks
        """
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
    
    def _clean_text(self, text):
        """
        Clean text by removing extra whitespace, etc.
        
        Args:
            text (str): Text to clean
            
        Returns:
            str: Cleaned text
        """
        # Replace multiple newlines with a single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


if __name__ == "__main__":
    # Example usage
    chunker = Chunker()
    
    # Test with a URL
    # chunks = chunker.process_url("https://example.com/article")
    
    # Test with a file
    # chunks = chunker.process_file("sample.pdf")
    
    # Print chunks
    # for i, chunk in enumerate(chunks):
    #     print(f"Chunk {i+1}:\n{chunk}\n{'='*50}\n") 