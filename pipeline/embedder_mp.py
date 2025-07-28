from pipeline.sectioner_pymupdf import extract_sections_from_pdf
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from typing import List
from schemas import Section, SentencedSection, SentenceSimilaritySection, SentenceSimilarity


def convert_to_sentences(sections: List[Section])-> List[SentencedSection]:
    # Converts each section's content into a list of sentences
    sections_in_sentences = []
    for section in sections:
        # Split by fullstop, then strip and filter out empty sentences
        sentences = [s.strip() for s in section.section_content.split(".") if s.strip()]
        section_obj = SentencedSection(
            document=section.document,
            section_title=section.section_title,
            section_content=sentences,
            page_number=section.page_number
        )
        sections_in_sentences.append(section_obj)
    return sections_in_sentences


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def get_embedding(text, tokenizer, model):
    encoded_input = tokenizer([text], padding=True, truncation=True, return_tensors='pt')
    with torch.no_grad():
        model_output = model(**encoded_input)
    emb = mean_pooling(model_output, encoded_input['attention_mask'])
    emb = F.normalize(emb, p=2, dim=1)
    return emb[0]


def check_sentences_for_persona_job_mp(pdf_path, persona_job) -> List[SentenceSimilaritySection]:
    """
    Multiprocessing-safe version that loads models within the function.
    Given a PDF path, extracts sections, splits into sentences, embeds each sentence,
    and checks cosine similarity with persona+job from input.json.
    Returns a list of dicts with sentence and similarity.
    """
    # Load models within the function to avoid multiprocessing issues
    tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
    model = AutoModel.from_pretrained('sentence-transformers/all-mpnet-base-v2')
    
    sections = extract_sections_from_pdf(pdf_path)
    sections_in_sentences = convert_to_sentences(sections)
    persona_job_emb = get_embedding(persona_job, tokenizer, model)
    results = []
    for section in sections_in_sentences:
        similarity_scores = []
        for sentence in section.section_content:
            sentence_emb = get_embedding(sentence, tokenizer, model)
            cosine_sim = torch.nn.functional.cosine_similarity(sentence_emb, persona_job_emb, dim=0).item()
            similarity_scores.append(SentenceSimilarity(
                sentence=sentence,
                cosine_similarity=cosine_sim
            ))
        results.append(SentenceSimilaritySection(
            document=section.document,
            section_title=section.section_title,
            section_content=similarity_scores,
            page_number=section.page_number
        ))
    return results
