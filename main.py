#!/usr/bin/env python3
"""
CPU-friendly Document Intelligence Pipeline
Extract and prioritize relevant document sections for specific personas and jobs-to-be-done.
"""

import time
import os
import json
import argparse
from typing import Optional, Dict, Any

from pipeline.loader import load_documents
from pipeline.chunker import chunk_documents
from pipeline.intelligent_extractor import IntelligentExtractor
from pipeline.embedder import rank_chunks, diversify_selection
from pipeline.summariser import summarize_top_chunks
from pipeline.schema import build_output, save_output, validate_output

def load_input_config(input_file: str = "input.json") -> Dict[str, Any]:
    """Load configuration from input.json file."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        persona = config.get("persona", {}).get("role", "Researcher")
        job = config.get("job_to_be_done", {}).get("task", "Analyze documents")
        documents = config.get("documents", [])
        
        return {
            "persona": persona,
            "job": job,
            "documents": documents,
            "challenge_info": config.get("challenge_info", {})
        }
        
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return None

def main(
    input_file: str = "input.json",
    data_path: str = "data/",
    output_path: str = "output.json",
    top_k: int = 10,
    final_k: int = 5,
    enable_diversification: bool = True,
    verbose: bool = False
):
    """Main pipeline execution function."""
    start_time = time.time()
    
    config = load_input_config(input_file)
    if not config:
        return False

    persona = config["persona"]
    job = config["job"]

    try:
        # Load documents
        docs = load_documents(data_path)
        if not docs:
            if verbose:
                print(f"❌ No PDF documents found in {data_path}")
            return False
        
        # Chunk documents
        chunks = chunk_documents(docs)
        
        # Intelligent content extraction
        extractor = IntelligentExtractor()
        chunks = extractor.extract_relevant_sections(chunks, persona, job)
        
        # Rank chunks
        top_chunks = rank_chunks(chunks, persona, job, top_k=top_k)
        
        # Apply diversification
        if enable_diversification and len(top_chunks) > final_k:
            top_chunks = diversify_selection(top_chunks, target_count=final_k)
        else:
            top_chunks = top_chunks[:final_k]
        
        # Summarize selected chunks
        refined = summarize_top_chunks(top_chunks, persona, job)
        
        # Generate output
        processing_time = time.time() - start_time
        processing_stats = {
            "total_documents": len(docs),
            "total_sections": sum(len(sections) for sections in docs.values()),
            "total_chunks": len(chunks),
            "selected_chunks": len(top_chunks),
            "processing_time_seconds": processing_time
        }
        
        output_json = build_output(
            doc_names=list(docs.keys()),
            persona=persona,
            job=job,
            top_chunks=top_chunks,
            summaries=refined,
            processing_stats=processing_stats
        )
        
        if not validate_output(output_json):
            if verbose:
                print("❌ Output validation failed")
            return False
        
        save_output(output_json, output_path)
        
        if verbose:
            print(f"✅ Processing completed in {processing_time:.2f}s")
            print(f"� Output saved to {output_path}")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"❌ Pipeline failed: {e}")
        return False

def create_sample_data_directory():
    """Create sample data directory with instructions."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document Intelligence Pipeline")
    parser.add_argument("--input", default="input.json", help="Input JSON file")
    parser.add_argument("--data-path", default="data/", help="PDF documents path")
    parser.add_argument("--output", default="output.json", help="Output JSON file")
    parser.add_argument("--top-k", type=int, default=10, help="Initial chunks to select")
    parser.add_argument("--final-k", type=int, default=5, help="Final chunks to summarize")
    parser.add_argument("--no-diversify", action="store_true", help="Disable diversification")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Input file '{args.input}' does not exist.")
        exit(1)
    
    if not os.path.exists(args.data_path):
        print(f"❌ Data path '{args.data_path}' does not exist.")
        exit(1)
    
    pdf_files = [f for f in os.listdir(args.data_path) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in '{args.data_path}'.")
        exit(1)
    
    success = main(
        input_file=args.input,
        data_path=args.data_path,
        output_path=args.output,
        top_k=args.top_k,
        final_k=args.final_k,
        enable_diversification=not args.no_diversify,
        verbose=args.verbose
    )
