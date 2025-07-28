# Adobe HackStreet Boys - Document Intelligence Pipeline

## 🎯 Solution Overview

This is a CPU-friendly document intelligence pipeline that extracts and prioritizes relevant document sections for specific personas and their job-to-be-done tasks. The solution processes PDF documents and returns the most relevant sections using semantic similarity.

## 📋 Requirements Compliance

- ✅ **Docker Platform**: Compatible with AMD64 (linux/amd64) architecture
- ✅ **CPU Only**: No GPU dependencies required
- ✅ **Model Size**: Uses `all-MiniLM-L6-v2` model (~90MB) - well under 200MB limit
- ✅ **Offline Operation**: Works without internet/network calls after model download
- ✅ **Multi-stage Build**: Optimized Dockerfile with build and runtime stages

## 🚀 Quick Start

### Build the Docker Image

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .
```

### Run the Solution

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  mysolutionname:somerandomidentifier
```

## 📁 Expected Directory Structure

Your input directory should contain:
```
input/
├── Collection 1/
│   ├── challenge1b_input.json
│   └── PDFs/
│       ├── document1.pdf
│       └── document2.pdf
├── Collection 2/
│   ├── challenge1b_input.json
│   └── PDFs/
│       └── documents...
└── Collection 3/
    ├── challenge1b_input.json
    └── PDFs/
        └── documents...
```

## 📤 Output

Results will be written to:
```
output/
├── Collection 1/
│   └── challenge1b_output.json
├── Collection 2/
│   └── challenge1b_output.json
└── Collection 3/
    └── challenge1b_output.json
```

## 🏗️ Architecture

### Multi-stage Dockerfile
- **Stage 1 (Builder)**: Installs build dependencies and Python packages
- **Stage 2 (Runtime)**: Minimal runtime environment with only necessary components

### Key Features
- **Semantic Similarity**: Uses sentence transformers for document relevance ranking
- **Multiprocessing**: Parallel processing for multiple collections
- **Memory Efficient**: Optimized for CPU-only operation
- **Security**: Runs as non-root user

### Models Used
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (~90MB)
- **PDF Processing**: PyMuPDF for text extraction
- **NLP**: Transformers library with CPU-optimized PyTorch

## 🛠️ Technical Details

### Dependencies
- Python 3.11
- PyMuPDF for PDF processing
- Transformers + PyTorch (CPU-only)
- Pydantic for data validation

### Processing Pipeline
1. **PDF Extraction**: Extract text and sections from PDFs
2. **Sentence Analysis**: Split content into sentences
3. **Semantic Embedding**: Generate embeddings for similarity comparison
4. **Ranking**: Score sections based on persona and job-to-be-done
5. **Output Generation**: Format results as structured JSON

### Performance
- **Memory Usage**: ~1-2GB RAM
- **Processing Time**: ~30-60 seconds per collection
- **Concurrent Processing**: Multi-collection parallel processing

## 🔧 Configuration

The solution automatically processes all collections found in the input directory. Each collection should have:
- `challenge1b_input.json` with persona and job description
- `PDFs/` directory with relevant PDF documents

## 📊 Output Format

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip for college friends",
    "processing_timestamp": "2025-07-28T22:00:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "section_title": "Planning Tips",
      "importance_rank": 1,
      "page_number": 3
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Relevant sentences grouped together...",
      "page_number": 3
    }
  ]
}
```

## 🧪 Testing

To test with the provided collections:
```bash
# Build
docker build --platform linux/amd64 -t adobe-hackstreet:test .

# Run with current directory as input
docker run --rm \
  -v "$(pwd):/app/input" \
  -v "$(pwd)/output:/app/output" \
  --network none \
  adobe-hackstreet:test
```

## 🏆 Team: HackStreet Boys

Built for the Adobe 1B Hackathon - delivering efficient, scalable document intelligence on CPU-only infrastructure.
