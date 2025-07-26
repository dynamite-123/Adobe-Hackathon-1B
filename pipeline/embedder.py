from sectioner_pymupdf import extract_sections_from_pdf
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F


def convert_to_sentences(sections):
    # Converts each section's content into a list of sentences
    sections_in_sentences = []
    for section in sections:
        sentences = section["section_content"].split(". ")
        new_section = section.copy()
        new_section["section_content"] = sentences
        sections_in_sentences.append(new_section)
    return sections_in_sentences


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

import json
import os

# Read persona and job to be done from input.json using absolute path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(SCRIPT_DIR, '..', 'input.json')
with open(INPUT_JSON_PATH, 'r') as f:
    input_data = json.load(f)
persona = input_data.get('persona', {}).get('role', '')
job_to_be_done = input_data.get('job_to_be_done', {}).get('task', '')
persona_job = f"{persona}. {job_to_be_done}"

# Load model from HuggingFace Hub
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

import os


# Use absolute path for data directory
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]


def get_embedding(text):
    encoded_input = tokenizer([text], padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    emb = mean_pooling(model_output, encoded_input['attention_mask'])
    emb = F.normalize(emb, p=2, dim=1)
    return emb[0]


def check_sentences_for_persona_job(pdf_path):
    """
    Given a PDF path, extracts sections, splits into sentences, embeds each sentence,
    and checks cosine similarity with persona+job from input.json.
    Returns a list of dicts with sentence and similarity.
    """
    sections = extract_sections_from_pdf(pdf_path)
    sections_in_sentences = convert_to_sentences(sections)
    persona_job_emb = get_embedding(persona_job)
    results = []
    for section in sections_in_sentences:
        similarity_scores = []
        for sentence in section["section_content"]:
            sentence_emb = get_embedding(sentence)
            cosine_sim = torch.nn.functional.cosine_similarity(sentence_emb, persona_job_emb, dim=0).item()
            similarity_scores.append({
                "sentence": sentence,
                "cosine_similarity": cosine_sim
            })
        results.append({
            "section_title": section.get("section_title", ""),
            "sentence_similarity": similarity_scores
        })
    return results


# if __name__ == "__main__":
    # for pdf_file in pdf_files:
    #     pdf_path = os.path.join(DATA_DIR, pdf_file)
    #     print(f"\nPDF: {pdf_file}")
    #     results = check_sentences_for_persona_job(pdf_path)
    #     for section in results:
    #         print(f"  Section: {section['section_title']}")
    #         for sim in section['sentence_similarity']:
    #             print(f"    Cosine: {sim['cosine_similarity']:.4f} | {sim['sentence']}")

# if __name__ == "__main__":
#     all_sims = []
#     for pdf_file in pdf_files:
#         pdf_path = os.path.join(DATA_DIR, pdf_file)
#         results = check_sentences_for_persona_job(pdf_path)
#         for section in results:
#             for sim in section['sentence_similarity']:
#                 all_sims.append({
#                     'pdf': pdf_file,
#                     'section': section['section_title'],
#                     'sentence': sim['sentence'],
#                     'cosine_similarity': sim['cosine_similarity']
#                 })
#     # Sort all sentences by similarity score (descending)
#     top_sims = sorted(all_sims, key=lambda x: x['cosine_similarity'], reverse=True)[:10]
#     print("Top 10 sentences most relevant to persona + job to be done:")
#     for i, item in enumerate(top_sims, 1):
#         print(f"{i}. PDF: {item['pdf']} | Section: {item['section']}\n   Cosine Similarity: {item['cosine_similarity']:.4f}\n   Sentence: {item['sentence']}")


if __name__ == "__main__":
    # ...existing code...
    # Print average similarity score for every section in every PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        results = check_sentences_for_persona_job(pdf_path)
        print(f"\nPDF: {pdf_file}")
        section_scores = []
        for section in results:
            sims = [sim['cosine_similarity'] for sim in section['sentence_similarity']]
            avg_score = sum(sims) / len(sims) if sims else 0.0
            section_scores.append({
                'section_title': section['section_title'],
                'avg_score': avg_score
            })
        # Sort sections by avg_score high to low
        section_scores_sorted = sorted(section_scores, key=lambda x: x['avg_score'], reverse=True)
        for sec in section_scores_sorted:
            print(f"  Section: {sec['section_title']}")
            print(f"    Average Cosine Similarity: {sec['avg_score']:.4f}")