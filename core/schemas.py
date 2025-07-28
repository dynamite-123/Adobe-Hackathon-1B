from typing import List
from pydantic import BaseModel, Field


# sectioner_pymupdf.py
class Section(BaseModel):
    document: str 
    section_title: str
    section_content: str
    page_number: int

# convert to sentences
class SentencedSection(BaseModel):
    document: str 
    section_title: str
    section_content: List[str]
    page_number: int

# check_sentences_for_persona_job
class SentenceSimilarity(BaseModel):
    sentence: str
    cosine_similarity: float

class SentenceSimilaritySection(BaseModel):
    document: str
    section_title: str
    section_content: List[SentenceSimilarity]
    page_number: int

class AverageSimilaritySection(BaseModel):
    avg_similarity: float
    document: str
    section_title: str
    section_content: List[SentenceSimilarity]
    page_number: int

class ExtractedSection(BaseModel):
    document: str
    section_title: str
    importance_rank: int
    page_number: int

class SubsectionAnalysis(BaseModel):
    document: str
    refined_text: str
    page_number: int

