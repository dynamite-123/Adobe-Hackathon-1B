import os
import json
from sectioner_pymupdf import main

data_dir = "data"
output_dir = "output_sections"
os.makedirs(output_dir, exist_ok=True)

pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith(".pdf")]
all_sections = {}

for pdf_file in pdf_files:
    pdf_path = os.path.join(data_dir, pdf_file)
    output_json = os.path.join(output_dir, pdf_file.replace(".pdf", "_sections.json"))
    main(pdf_path, output_json)
    with open(output_json, "r", encoding="utf-8") as f:
        sections = json.load(f)
    all_sections[pdf_file] = sections

# Write all sections to a single JSON file
with open("all_pdfs_sections.json", "w", encoding="utf-8") as f:
    json.dump(all_sections, f, indent=2, ensure_ascii=False)

print(f"Processed {len(pdf_files)} PDFs. Combined sections written to all_pdfs_sections.json.")
