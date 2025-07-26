import fitz  # PyMuPDF
import re
import os
import json


def extract_pdf_contents(pdf_path):
    """
    Extracts and returns the text contents of a PDF file using PyMuPDF.
    Args:
        pdf_path (str): Path to the PDF file.
    Returns:
        List[Dict]: List of dicts with text, font size, font name, and page number.
    """
    doc = fitz.open(pdf_path)
    lines_data = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")['blocks']
        for b in blocks:
            if b['type'] == 0:  # text block
                for l in b['lines']:
                    line_text = " ".join([span['text'] for span in l['spans']]).strip()
                    if line_text:
                        # Use the largest font size in the line
                        font_size = max(span['size'] for span in l['spans'])
                        font_names = list(set(span['font'] for span in l['spans']))
                        lines_data.append({
                            "text": line_text,
                            "font_size": font_size,
                            "font_names": font_names,
                            "page": page_num
                        })
    return lines_data


if __name__ == "__main__":
    sample_pdf = "data/South of France - Cities.pdf"
    lines = extract_pdf_contents(sample_pdf)
    print(json.dumps(lines, indent=2, ensure_ascii=False))

