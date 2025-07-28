import json
import os
import sys
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import asyncio

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add parent directory to path 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedder import check_sentences_for_persona_job
from generate_output import get_top_5_sections, get_top_5_sentence_groups_per_section, get_extracted_sections


def process_trip_planning_input_sequential(input_data):
    """
    Sequential version for comparison - this is your original working version
    """
    # Extract metadata
    metadata = {
        "input_documents": [doc["filename"] for doc in input_data["documents"]],
        "persona": input_data["persona"]["role"],
        "job_to_be_done": input_data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now().isoformat()
    }

    # Aggregate results from all PDFs
    all_sections = []
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    persona_job_query = metadata["persona"] + " " + metadata["job_to_be_done"]
    
    print(f"Processing {len(input_data['documents'])} documents sequentially...")
    
    for i, doc in enumerate(input_data["documents"], 1):
        pdf_path = os.path.join(data_dir, doc['filename'])
        try:
            print(f"Processing {i}/{len(input_data['documents'])}: {doc['filename']}...")
            results = check_sentences_for_persona_job(pdf_path, persona_job_query)
            all_sections.extend(results)
            print(f"Completed {doc['filename']} - found {len(results)} sections")
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    print(f"Total sections collected: {len(all_sections)}")

    # Get top 5 sections (AverageSimilaritySection)
    top5_avg_sections = get_top_5_sections(all_sections)

    # Get extracted_sections (ExtractedSection)
    extracted_sections = get_extracted_sections(top5_avg_sections)
    extracted_sections_dicts = [sec.model_dump() for sec in extracted_sections]

    # Get subsection_analysis (SubsectionAnalysis)
    subsection_analysis = get_top_5_sentence_groups_per_section(top5_avg_sections)
    subsection_analysis_dicts = [sub.model_dump() for sub in subsection_analysis]

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections_dicts,
        "subsection_analysis": subsection_analysis_dicts
    }
    return output


def process_trip_planning_input_optimized(input_data):
    """
    Optimized version with better memory management and progress tracking
    """
    # Extract metadata
    metadata = {
        "input_documents": [doc["filename"] for doc in input_data["documents"]],
        "persona": input_data["persona"]["role"],
        "job_to_be_done": input_data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now().isoformat()
    }

    # Aggregate results from all PDFs
    all_sections = []
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    persona_job_query = metadata["persona"] + " " + metadata["job_to_be_done"]
    
    print(f"Processing {len(input_data['documents'])} documents with optimizations...")
    
    # Process documents with progress tracking
    for i, doc in enumerate(input_data["documents"], 1):
        pdf_path = os.path.join(data_dir, doc['filename'])
        try:
            start_time = datetime.now()
            print(f"[{i}/{len(input_data['documents'])}] Starting {doc['filename']}...")
            
            results = check_sentences_for_persona_job(pdf_path, persona_job_query)
            all_sections.extend(results)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"[{i}/{len(input_data['documents'])}] Completed {doc['filename']} in {duration:.1f}s - found {len(results)} sections")
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")

    print(f"Total sections collected: {len(all_sections)}")

    # Get top 5 sections (AverageSimilaritySection)
    top5_avg_sections = get_top_5_sections(all_sections)

    # Get extracted_sections (ExtractedSection)
    extracted_sections = get_extracted_sections(top5_avg_sections)
    extracted_sections_dicts = [sec.model_dump() for sec in extracted_sections]

    # Get subsection_analysis (SubsectionAnalysis)
    subsection_analysis = get_top_5_sentence_groups_per_section(top5_avg_sections)
    subsection_analysis_dicts = [sub.model_dump() for sub in subsection_analysis]

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections_dicts,
        "subsection_analysis": subsection_analysis_dicts
    }
    return output


if __name__ == "__main__":
    start = datetime.now()
    
    input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input.json')
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output.json')
    
    with open(input_path, 'r') as f:
        input_data = json.load(f)
    
    # Use the optimized sequential version
    result = process_trip_planning_input_optimized(input_data)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    end = datetime.now()
    print(f"Processing completed in {end - start}")
