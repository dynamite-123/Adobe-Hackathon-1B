# 🧠 CPU-friendly Document Intelligence Pipeline

Extract and prioritize relevant document sections for specific personas and their job-to-be-done.

## 🎯 Overview

This pipeline processes PDF documents and extracts the most relevant sections based on:
- **Persona**: Target user (e.g., "PhD Researcher in Computational Biology")
- **Job-to-be-done**: Specific task (e.g., "Prepare a comprehensive literature review")

## ⚡ Features

- **CPU-only processing** - No GPU required
- **Lightweight models** - All models ≤ 1GB
- **Fast processing** - ≤ 60s for 3-5 PDFs
- **Structured output** - JSON format with validation
- **Modular design** - Easy to customize and extend

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone/navigate to project directory
cd HackStreet-Boys-Adobe-1B

# Install dependencies
pip install -r requirements.txt
```

### 2. Add PDF Documents

```bash
# Create data directory and add your PDFs
mkdir -p data/
# Copy your PDF files to data/
```

### 3. Run Pipeline

```bash
# Basic usage with default settings
python main.py

# Custom parameters
python main.py --top-k 15 --final-k 8 --verbose

# See all options
python main.py --help
```

## 📦 Pipeline Steps

1. **📥 PDF Loading**: Extract text using PyMuPDF with header detection
2. **🔧 Chunking**: Split into 300-500 token sections with overlap
3. **🤖 Intelligent Filtering**: Remove irrelevant content using NLP models
4. **🔍 Embedding**: Rank chunks using semantic similarity
5. **🎲 Diversification**: Balance relevance and diversity (optional)
6. **📝 Summarization**: Generate persona-specific summaries
7. **📋 Output**: Structured JSON with metadata and analysis

## 📊 Output Format

```json
{
  "metadata": {
    "input_documents": ["paper1.pdf", "paper2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare literature review...",
    "processing_timestamp": "2025-07-26T11:45:00",
    "processing_stats": {
      "total_documents": 3,
      "total_chunks": 156,
      "selected_chunks": 5,
      "processing_time_seconds": 42.3
    }
  },
  "extracted_sections": [
    {
      "document": "paper1.pdf",
      "section_title": "Model Architecture",
      "page_number": 3,
      "importance_rank": 1
    }
  ]
}
```

## ⚙️ Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--input` | `input.json` | Configuration file |
| `--data-path` | `data/` | Directory containing PDF files |
| `--output` | `output.json` | Output file path |
| `--top-k` | `10` | Initial chunks to select |
| `--final-k` | `5` | Final chunks to summarize |
| `--no-diversify` | `False` | Disable diversity selection |
| `--verbose` | `False` | Enable detailed output |

## 🏗️ Architecture

### Core Modules

- **`loader.py`**: PDF text extraction with section detection
- **`chunker.py`**: Intelligent text chunking with overlap
- **`intelligent_extractor.py`**: NLP-based relevance filtering
- **`embedder.py`**: Semantic ranking and diversity selection  
- **`summariser.py`**: Context-aware summarization
- **`schema.py`**: Output validation and formatting

### Models Used

- **Embedding**: `all-MiniLM-L6-v2` (~90MB)
- **Summarization**: `t5-small` (~242MB)
- **Classification**: `nlptown/bert-base-multilingual` (~400MB)

## 🧪 Example Use Cases

### Academic Research
```bash
python main.py \
    --verbose \
    --final-k 8
```

### Industry Analysis
```bash
python main.py \
    --top-k 15 \
    --final-k 6 \
    --no-diversify
```

### Technical Review
```bash
python main.py \
    --verbose \
    --final-k 3
```

## 🔧 Customization

### Adding New Models

Edit the model definitions in:
- `intelligent_extractor.py`: Change classification model
- `embedder.py`: Change embedding model
- `summariser.py`: Change summarization model

### Custom Section Detection

Modify `loader.py`:
```python
header_patterns = [
    r'^(\d+\.?\s+[A-Z][^.\n]*)',  # Add your patterns
    # ... existing patterns
]
```

### Output Format

Extend models in `schema.py` for additional fields.

## 📈 Performance

**Typical performance** (3-5 PDFs, ~50 pages total):
- Loading: ~5s
- Chunking: ~2s  
- Intelligence filtering: ~10s
- Embedding: ~15s
- Summarization: ~15s
- **Total: ~45s**

**Memory usage**: ~1.2GB RAM peak

## 🚫 Constraints

- **CPU-only**: No GPU acceleration required
- **Model size**: All models ≤ 1GB
- **Processing time**: ≤ 60s for typical workloads
- **Offline**: No internet required during runtime
- **Text PDFs**: Requires extractable text (not image-only PDFs)

## 🐛 Troubleshooting

### Common Issues

1. **No PDFs found**: Ensure `.pdf` files are in the data directory
2. **Long processing time**: Reduce `--top-k` and `--final-k` values
3. **Memory errors**: Process fewer documents at once
4. **Poor extraction**: PDFs may be image-based or have complex layouts

### Verbose Mode

```bash
# Enable detailed output for debugging
python main.py --verbose
```

## 📄 License

This project is part of the HackStreet Boys Adobe 1B hackathon submission.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ for efficient document intelligence on CPU-only systems**