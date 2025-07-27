from schemas import SentenceSimilaritySection, AverageSimilaritySection, SubsectionAnalysis, ExtractedSection
from typing import List

def get_top_5_sections(results: List[SentenceSimilaritySection]) -> List[AverageSimilaritySection]:
    """
    Given results from check_sentences_for_persona_job, returns top 5 sections
    by average of the top three cosine similarity scores.
    """
    avg_sections = []
    for section in results:
        sims = [sim.cosine_similarity for sim in section.section_content]
        top3 = sorted(sims, reverse=True)[:3]
        avg_sim = sum(top3) / len(top3) if top3 else 0.0
        avg_sections.append(AverageSimilaritySection(
            avg_similarity=avg_sim,
            document=section.document,
            section_title=section.section_title,
            section_content=section.section_content,
            page_number=section.page_number
        ))
    # Sort by avg_similarity and return top 5
    return sorted(avg_sections, key=lambda x: x.avg_similarity, reverse=True)[:5]

def get_extracted_sections(results: List[AverageSimilaritySection]) -> List[ExtractedSection]:
    """
    Given AverageSimilaritySection results, returns top 5 ExtractedSection objects by avg_similarity.
    """
    return [
        ExtractedSection(
            document=section.document,
            section_title=section.section_title,
            importance_rank=i + 1,
            page_number=section.page_number
        )
        for i, section in enumerate(sorted(results, key=lambda x: x.avg_similarity, reverse=True)[:5])
    ]


def get_top_5_sentence_groups_per_section(results: List[AverageSimilaritySection]) -> List[SubsectionAnalysis]:
    """
    For each section, finds the top 5 individual sentences by cosine similarity and groups them together.
    Returns the top 5 groups (one per section) with the highest average similarity.
    Each group contains: section_title, sentences (list), avg_similarity.
    """
    analyses = []
    for section in results:
        sims = section.section_content
        # Get top 5 sentences by cosine_similarity
        top5_sims = sorted(sims, key=lambda x: x.cosine_similarity, reverse=True)[:5]
        merged_text = " ".join([s.sentence for s in top5_sims])
        analyses.append(SubsectionAnalysis(
            document=section.document,
            refined_text=merged_text,
            page_number=section.page_number
        ))
    return analyses
