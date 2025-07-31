# Adobe HackStreet Boys - Document Intelligence Pipeline

Extract and prioritize relevant document sections for specific personas and their job-to-be-done.

## Project Overview

This is a *CPU-friendly document intelligence pipeline* that processes PDF documents and extracts the most relevant sections using semantic similarity. The system analyzes documents based on a specific persona (e.g., "Travel Planner") and their job-to-be-done (e.g., "Plan a 4-day trip for college friends").

## Project Structure


HackStreet-Boys-Adobe-1BAni/
├── core/                          # Main processing engine
│   ├── __init__.py                   # Module initialization
│   ├── embedder.py                   # Semantic embedding & similarity
│   ├── sectioner_pymupdf.py          # PDF text extraction
│   ├── schemas.py                    # Data models (Pydantic)
│   ├── format.py                     # Single-threaded processing
│   ├── format_mp.py                  # Multi-threaded processing
│   ├── process_collections.py        # Sequential collection processing
│   ├── process_collections_mp.py     # Parallel collection processing
│   ├── generate_output.py            # Output formatting & ranking
│   └── requirements.txt              # Python dependencies
│
├── Collection 1/                  # Example collection
│   ├── challenge1b_input.json       # Input configuration
│   ├── challenge1b_output.json      # Generated results (after processing)
│   └── PDFs/                        # Source documents
│       ├── document1.pdf
│       ├── document2.pdf
│       └── ... (your PDF files)
│
├── Dockerfile                     # Multi-stage container build
├── docker-compose.yml             # Container orchestration
├── .dockerignore                  # Build context exclusions
├── README.md                      # This file
└── .gitignore                     # Git exclusions


## Docker Commands & Usage

### Build Commands

```bash
# Standard build (for competition submission)
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

### Run Commands

```bash
# Competition format (as required) - Linux/Mac
docker run --rm \
  -v $(pwd):/app/collections \
  --network none \
  mysolutionname:somerandomidentifier

# Competition format (as required) - Windows PowerShell
docker run --rm -v "${PWD}:/app/collections" --network none mysolutionname:somerandomidentifier

# Check results in Collection*/
ls Collection*/
```

## Features & Capabilities

- *CPU-only processing* - No GPU required, optimized for standard hardware
- *Lightweight models* - Uses all-MiniLM-L6-v2 under 1GB limit
- *Fast processing* - ~30-60 seconds for full collections
- *Parallel processing* - Multi-collection and multi-document processing
- *Structured output* - JSON format with Pydantic validation
- *Containerized* - Docker multi-stage build for production deployment
- *Secure* - Runs as non-root user, offline-capable

## How It Works

### Processing Pipeline

1. *PDF Loading*: Extract text and detect sections using PyMuPDF
2. *Sentence Splitting*: Break content into individual sentences
3. *Semantic Embedding*: Generate vector representations using transformers
4. *Similarity Scoring*: Compare against persona + job-to-be-done query
5. *Ranking & Selection*: Pick top 5 most relevant sections
6. *Output Generation*: Format as structured JSON

### Input Format (challenge1b_input.json)

```json
{
  "persona": {
    "role": "Travel Planner"
  },
  "job_to_be_done": {
    "task": "Plan a trip of 4 days for a group of 10 college friends."
  },
  "documents": [
    {"filename": "document1.pdf", "title": "Cities Guide"},
    {"filename": "document2.pdf", "title": "Food Guide"}
  ]
}
```

### Output Format (challenge1b_output.json)

```json
{
  "metadata": {
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-28T22:00:00"
  },
  "extracted_sections": [
    {
      "document": "document1.pdf",
      "section_title": "Planning and Exploring",
      "importance_rank": 1,
      "page_number": 0
    }
  ],
  "subsection_analysis": [
    {
      "document": "document1.pdf", 
      "refined_text": "Planning a trip requires thoughtful preparation...",
      "page_number": 0
    }
  ]
}
```

## Technical Architecture

### Core Components

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| embedder.py | Semantic similarity | check_sentences_for_persona_job() |
| sectioner_pymupdf.py | PDF extraction | extract_sections_from_pdf() |
| generate_output.py | Ranking & output | get_top_5_sections() |
| process_collections_mp.py | Multi-processing | main() (entry point) |
| schemas.py | Data validation | Pydantic models |

### Models Used

- *Embedding*: sentence-transformers/all-MiniLM-L6-v2
- *PDF Processing*: PyMuPDF (fast, lightweight)
- *Data Validation*: Pydantic v2.9+
- *Deep Learning*: PyTorch CPU-only

### Performance Specs

- *Memory Usage*: ~1-2GB RAM peak
- *Processing Time*: 30-60 seconds per collection
- *Model Loading*: ~5-10 seconds initial startup
- *Concurrent Collections*: Up to CPU core count

## Troubleshooting

### Common Docker Issues

```bash
# Permission issues on Linux/Mac
docker run --rm --user $(id -u):$(id -g) ...

# Network debugging (remove --network none)
docker run --rm -v $(pwd):/app/collections mysolutionname:somerandomidentifier
```

### Common Processing Issues

| Issue | Solution |
|-------|----------|
| "No collections found" | Ensure directories named Collection 1, Collection 2, etc. exist |
| "PDF extraction failed" | Check PDFs are text-based, not image-only |
| "Model download timeout" | Run once with internet, then use --network none |
| "Memory error" | Reduce batch size or process collections sequentially |

## Performance Benchmarks

*Test Environment*: 4-core CPU, 8GB RAM, SSD storage

| Collection | Documents | Pages | Processing Time |
|------------|-----------|-------|-----------------|
| Collection 1 (Example) | 7 PDFs | ~35 pages | 45 seconds |
| *Total* | *7 PDFs* | *~35 pages* | *~45 seconds* |

## Team: HackStreet Boys

Built for the *Adobe 1B Hackathon* - delivering efficient, scalable document intelligence on CPU-only infrastructure.

### Key Innovations

- *Multi-stage Docker builds* for optimized deployment  
- *Parallel processing* for multiple document collections  
- *Semantic similarity* using lightweight transformer models  
- *CPU-only architecture* with no GPU dependencies  
- *Offline operation* with pre-downloaded models  

---

*Ready to process your documents? Try the Docker commands above!*