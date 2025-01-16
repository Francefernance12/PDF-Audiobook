from PyPDF2 import PdfReader
import re

# Function to clean up the text for better readability for user and tts
def clean_text(text):
    # Add space between a lowercase followed by an uppercase letter (camelCase or joined words)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Add space between a number and a letter
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Add proper spacing after periods
    text = re.sub(r'\.(?=[A-Z])', '. ', text)
    
    # Add proper spacing after commas
    text = re.sub(r',(?=\w)', ', ', text)
    
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    
    # Ensure proper spacing between sentences
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
    
    # Fix common PDF artifacts where words are joined
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
    
    # Handle special characters that might appear in PDFs
    text = text.replace('ﬁ', 'fi')  # Replace special fi ligature
    text = text.replace('ﬂ', 'fl')  # Replace special fl ligature
    text = text.replace('–', '-')   # Normalize dashes
    text = text.replace('—', '-')   # Normalize em dashes
    
    return text.strip()

def loadPDF(filename):
    try:
        text = ""
        reader = PdfReader(filename)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += clean_text(page_text) + "\n\n"  # Add double newline between pages

        if text is not None:
            if len(text.encode('utf-8')) > 5000:
                print("Text is too long. Limiting to 5000 characters.")
                text = text[:5000]  # Limit to 5000 characters
                print(text)
            return text
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

