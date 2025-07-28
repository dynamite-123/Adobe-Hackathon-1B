import os
import glob
import json
from . import format
from datetime import datetime

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
    for collection in collections:
        collection_path = os.path.join(root_dir, collection)
        print(f'Processing {collection_path}...')
        process_collection(collection_path)
    print('All collections processed.')

if __name__ == '__main__':
    start = datetime.now()
    main()
    end = datetime.now()

    print(f"Processing completed in {end - start} seconds")
