import os
import glob
import json
from . import format
from datetime import datetime
from multiprocessing import Pool, cpu_count

# Root directory containing collections
def get_collection_dirs(root_dir):
    return [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.startswith('Collection')]

def process_collection(collection_path):
    input_json_name = 'challenge1b_input.json'
    input_json_path = os.path.join(collection_path, input_json_name)
    output_json_name = input_json_name.replace('input', 'output')
    output_json_path = os.path.join(collection_path, output_json_name)
    if not os.path.exists(input_json_path):
        print(f"Input JSON not found: {input_json_path}")
        return
    with open(input_json_path, 'r') as f:
        input_data = json.load(f)
    
    # Update the document filenames to include full paths to PDFs
    pdf_dir = os.path.join(collection_path, 'PDFs')
    for doc in input_data["documents"]:
        doc['filename'] = os.path.join(pdf_dir, doc['filename'])
    
    result = format.process_trip_planning_input(input_data)
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=2)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    collections = get_collection_dirs(root_dir)
    
    if not collections:
        print("No collections found.")
        return
    
    # Prepare collection paths
    collection_paths = [os.path.join(root_dir, collection) for collection in collections]
    
    print(f"Found {len(collections)} collections to process.")
    print(f"Using {min(len(collections), cpu_count())} processes.")
    
    # Use multiprocessing to process collections in parallel
    with Pool(processes=min(len(collections), cpu_count())) as pool:
        # Map the process_collection function to all collection paths
        pool.map(process_collection_with_logging, collection_paths)
    
    print('All collections processed.')

def process_collection_with_logging(collection_path):
    """Wrapper function to add logging for multiprocessing"""
    print(f'Processing {collection_path}...')
    try:
        process_collection(collection_path)
        print(f'Completed {collection_path}')
    except Exception as e:
        print(f'Error processing {collection_path}: {str(e)}')

if __name__ == '__main__':
    start = datetime.now()
    main()
    end = datetime.now()

    print(f"Processing completed in {end - start} seconds")
