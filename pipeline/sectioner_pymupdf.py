import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict
import argparse
import json
import os


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
                sections.append({
                    "document": doc_name,
                    "section_title": current_section,
                    "section_content": "\n".join(current_content).strip(),
                    "page": current_page
                })
                current_content = []
            current_section = line["text"].strip()
            current_page = line["page"]
        else:
            current_content.append(line["text"])
    if current_section:
        sections.append({
            "document": doc_name,
            "section_title": current_section,
            "section_content": "\n".join(current_content).strip(),
            "page": current_page
        })
    return sections

# def main(pdf_path, output_path):
#     print(f"[INFO] Extracting and structuring sections from: {pdf_path}")
#     sections = heading_based_sections(pdf_path)
#     if not sections:
#         print("[ERROR] No sections found in PDF.")
#         return
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(sections, f, indent=2, ensure_ascii=False)
#     print(f"Structured sections written to {output_path}")

# if __name__ == "__main__":
#     sample_pdf = "data/South of France - Cities.pdf"
#     sample_output = "demo_sections_structured.json"
#     main(sample_pdf, sample_output)

