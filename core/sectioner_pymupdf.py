import fitz  # PyMuPDF
import os
import re
from core.schemas import Section
from typing import List


def clean_text(text):
    """Clean text by removing unwanted Unicode characters and normalizing whitespace."""
    if not text:
        return ""
    
    # First, handle Unicode ligatures and special combinations
    text = re.sub(r'\ufb00', 'ff', text)  # ff ligature
    text = re.sub(r'\ufb01', 'fi', text)  # fi ligature
    text = re.sub(r'\ufb02', 'fl', text)  # fl ligature
    text = re.sub(r'\ufb03', 'ffi', text)  # ffi ligature
    text = re.sub(r'\ufb04', 'ffl', text)  # ffl ligature
    text = re.sub(r'\ufb05', 'ft', text)   # ft ligature
    text = re.sub(r'\ufb06', 'st', text)   # st ligature
    
    # Handle Unicode escape sequences that should be converted to proper characters
    # Common smart quotes and apostrophes
    text = re.sub(r'[\u2018\u2019]', "'", text)  # Smart single quotes to regular apostrophe
    text = re.sub(r'[\u201C\u201D]', '"', text)  # Smart double quotes to regular quotes
    text = re.sub(r'[\u2013\u2014]', '-', text)  # En dash and em dash to regular dash
    text = re.sub(r'[\u2026]', '...', text)  # Ellipsis to three dots
    
    # Remove common Unicode bullet points and special characters
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', '', text)  # Various bullet points
    text = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)  # Zero-width characters
    text = re.sub(r'[\u00A0]', ' ', text)  # Non-breaking space to regular space
    
    # Remove other problematic Unicode characters that might appear as \u sequences
    text = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', text)  # Control characters
    
    # Handle any remaining Unicode escape sequences that might be literal \u codes in the text
    # This catches cases where the text contains literal "\u2022" strings instead of the actual character
    text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
    
    # Clean up any "o " patterns that might be leftover bullet formatting
    text = re.sub(r'\bo\s+', '', text)  # Remove standalone "o " (often from bullet points)
    
    # Handle common OCR/PDF extraction errors
    text = re.sub(r'o\ufb04ine', 'offline', text)  # Specific fix for "offline"
    text = re.sub(r'o\ufb03ce', 'office', text)    # Specific fix for "office"
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text


def extract_lines_with_fonts(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if b['type'] == 0:
                for l in b['lines']:
                    line_text = " ".join([span['text'] for span in l['spans']]).strip()
                    cleaned_text = clean_text(line_text)
                    if cleaned_text:  # Only include lines with meaningful content after cleaning
                        font_names = list(set(span['font'] for span in l['spans']))
                        font_size = max(span['size'] for span in l['spans'])
                        lines.append({
                            "text": cleaned_text,
                            "font_names": font_names,
                            "font_size": font_size,
                            "page": page_num
                        })
    return lines

def is_heading(line):
    """
    Determine if a line is likely a heading based on font properties and text characteristics.
    """
    font_names = set(line.get("font_names", []))
    text = line["text"].strip()
    
    # Skip empty text
    if not text:
        return False
    
    # Skip very short single words or very long text
    word_count = len(text.split())
    if word_count < 2 or word_count > 10:
        return False
    
    # Check for bold font indicators
    is_bold = any(bold_indicator in font_name for font_name in font_names 
                  for bold_indicator in ["Bold", "bold", "BOLD"])
    
    # Skip lines that end with colons (likely not section headers)
    if text.endswith(":"):
        return False
    
    # Skip lines that are clearly content rather than headers
    if len(text) > 100:  # Very long lines are likely content
        return False
    
    return is_bold and text

def should_include_line(text):
    """
    Determine if a line should be included in the content.
    Filters out lines that are just artifacts or unwanted characters.
    """
    if not text or not text.strip():
        return False
    
    # Skip lines that are just single characters or very short
    if len(text.strip()) < 3:
        return False
    
    # Skip lines that are mostly punctuation or numbers
    if re.match(r'^[\s\d\W]{1,5}$', text.strip()):
        return False
    
    # Skip lines that start with common bullet artifacts
    stripped = text.strip()
    if stripped.startswith(('o ', '• ', '- ', '* ')):
        # Check if it's just the bullet with very little content
        content_after_bullet = stripped[2:].strip()
        if len(content_after_bullet) < 5:
            return False
    
    # Skip lines that are just standalone single letters or words
    if re.match(r'^[a-zA-Z]\s*$', stripped):
        return False
    
    return True


def post_process_section_content(content):
    """
    Apply final cleaning and formatting to section content.
    """
    if not content:
        return ""
    
    # Split into lines for processing
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Additional cleaning for common patterns
        # Remove standalone "o" at the beginning of lines (bullet artifacts)
        line = re.sub(r'^o\s+', '', line)
        
        # Clean up any remaining escape sequences
        line = clean_text(line)
        
        # Additional specific fixes for common OCR errors
        line = re.sub(r'\boffi\s*ce\b', 'office', line)  # office split across ligatures
        line = re.sub(r'\boff\s*line\b', 'offline', line)  # offline split
        
        # Fix common word boundary issues
        line = re.sub(r'\s+', ' ', line)  # Multiple spaces to single space
        
        # Only keep lines that have meaningful content
        if should_include_line(line):
            processed_lines.append(line)
    
    # Final pass to clean up the entire content
    result = '\n'.join(processed_lines).strip()
    
    # Apply final cleaning to the entire content
    result = clean_text(result)
    
    return result


def extract_sections_from_pdf(pdf_path):
    doc_name = os.path.basename(pdf_path)
    lines = extract_lines_with_fonts(pdf_path)
    sections = []
    current_section = None
    current_content = []
    current_page = 0
    for line in lines:
        if is_heading(line):
            if current_section:
                # Filter and clean content before creating section
                filtered_content = [content for content in current_content 
                                  if should_include_line(content)]
                if filtered_content:  # Only create section if there's meaningful content
                    section_content = post_process_section_content('\n'.join(filtered_content))
                    if section_content:  # Double-check after post-processing
                        section_obj = Section(
                            document=doc_name,
                            section_title=current_section,
                            section_content=section_content,
                            page_number=current_page
                        )
                        sections.append(section_obj)
                current_content = []
            current_section = clean_text(line["text"].strip())
            current_page = line["page"]
        else:
            # Add line to content if it passes the filtering
            if should_include_line(line["text"]):
                current_content.append(line["text"])
    
    if current_section:
        # Filter and clean content before creating final section
        filtered_content = [content for content in current_content 
                          if should_include_line(content)]
        if filtered_content:  # Only create section if there's meaningful content
            section_content = post_process_section_content('\n'.join(filtered_content))
            if section_content:  # Double-check after post-processing
                section_obj = Section(
                    document=doc_name,
                    section_title=current_section,
                    section_content=section_content,
                    page_number=current_page
                )
                sections.append(section_obj)
    return sections

def extract_all_sections(data_dir) -> List[Section]:
    """
    Extracts sections from all PDF documents in the given directory.
    Returns a list of dicts: document, section_title, section_content, page_number.
    """
    sections = []
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(data_dir, pdf_file)
        doc_sections = extract_sections_from_pdf(pdf_path)
        for sec in doc_sections:
            sections.append(sec)
    return sections


if __name__ == "__main__":
    import json
    
    # Test with one PDF from Collection 3
    test_pdf_path = "/home/dev/programming/projects/HackStreet-Boys-Adobe-1B/Collection 3/PDFs/Breakfast Ideas.pdf"
    
    print(f"Testing PDF extraction with: {test_pdf_path}")
    print("=" * 50)
    
    try:
        sections = extract_sections_from_pdf(test_pdf_path)
        
        # Convert sections to JSON-serializable format
        sections_data = []
        for section in sections:
            sections_data.append({
                "document": section.document,
                "section_title": section.section_title,
                "section_content": section.section_content,
                "page_number": section.page_number
            })
        
        # Print as JSON
        print(json.dumps(sections_data, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

