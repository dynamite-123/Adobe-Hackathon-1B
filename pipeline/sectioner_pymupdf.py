import fitz  # PyMuPDF
import os
from schemas import Section
from typing import List


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
                    if line_text:
                        font_names = list(set(span['font'] for span in l['spans']))
                        font_size = max(span['size'] for span in l['spans'])
                        lines.append({
                            "text": line_text,
                            "font_names": font_names,
                            "font_size": font_size,
                            "page": page_num
                        })
    return lines

def is_heading(line):
    # Heuristic: bold font, short text, not a bullet, not empty
    font_names = set(line.get("font_names", []))
    text = line["text"].strip()
    return (
        ("Bold" in font_names or "AdobeClean-Bold" in font_names) and
        1 < len(text.split()) <= 10 and
        not text.startswith("\u2022") and
        text and not text.endswith(":")
    )

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
                section_obj = Section(
                    document=doc_name,
                    section_title=current_section,
                    section_content="\n".join(current_content).strip(),
                    page_number=current_page
                )
                sections.append(section_obj)
                current_content = []
            current_section = line["text"].strip()
            current_page = line["page"]
        else:
            current_content.append(line["text"])
    if current_section:
        section_obj = Section(
            document=doc_name,
            section_title=current_section,
            section_content="\n".join(current_content).strip(),
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

