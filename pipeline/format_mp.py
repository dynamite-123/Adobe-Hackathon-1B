
import json
import os
import sys
from datetime import datetime
from multiprocessing import Pool
from functools import partial

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Add parent directory to path 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedder import check_sentences_for_persona_job
from generate_output import get_top_5_sections, get_top_5_sentence_groups_per_section, get_extracted_sections


def process_single_document_safe(doc_filename, data_dir, persona_job_query):
    """
    Process a single document with error handling.
    This version imports the embedder inside the function to avoid serialization issues.
    """
    # Import inside the function to avoid multiprocessing serialization issues
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from embedder import check_sentences_for_persona_job
    
    pdf_path = os.path.join(data_dir, doc_filename)
    try:
        print(f"Processing {doc_filename}...")
        results = check_sentences_for_persona_job(pdf_path, persona_job_query)
        print(f"Completed {doc_filename} - found {len(results)} sections")
        return results
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []


def process_trip_planning_input(input_data, num_processes=None):
    # Extract metadata
    metadata = {
        "input_documents": [doc["filename"] for doc in input_data["documents"]],
        "persona": input_data["persona"]["role"],
        "job_to_be_done": input_data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now().isoformat()
    }

    # Aggregate results from all PDFs using multiprocessing
    all_sections = []
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    persona_job_query = metadata["persona"] + " " + metadata["job_to_be_done"]
    
    # Use multiprocessing for parallel document processing
    if num_processes is None:
        # Limit to 2-3 processes to avoid memory issues with transformer models
        num_processes = min(3, len(input_data["documents"]))
    
    print(f"Processing {len(input_data['documents'])} documents using {num_processes} processes...")
    
    # Prepare arguments for multiprocessing - just pass filenames
    doc_filenames = [doc['filename'] for doc in input_data["documents"]]
    
    # Create a partial function with fixed arguments
    process_func = partial(process_single_document_safe, 
                          data_dir=data_dir, 
                          persona_job_query=persona_job_query)
    
    try:
        # Use multiprocessing
        with Pool(processes=num_processes) as pool:
            # Map the processing function to all documents
            results_list = pool.map(process_func, doc_filenames)
        
        # Flatten the results
        for results in results_list:
            all_sections.extend(results)
    except Exception as e:
        print(f"Multiprocessing failed: {e}")
        print("Falling back to sequential processing...")
        # Fallback to sequential processing
        for filename in doc_filenames:
            results = process_func(filename)
            all_sections.extend(results)

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
    # This guard is essential for multiprocessing on Windows and prevents infinite recursion
    input_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'input.json')
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output.json')
    with open(input_path, 'r') as f:
        input_data = json.load(f)
    result = process_trip_planning_input(input_data)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)

    end = datetime.now()

    print(f"Processing completed in {end - start} seconds")
