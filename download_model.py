#!/usr/bin/env python3
"""
Script to pre-download and cache the sentence-transformers model during Docker build.
This ensures the model is available offline during container execution.
"""
import os
from transformers import AutoTokenizer, AutoModel

# Set cache directory to a location that will be preserved
cache_dir = "/home/app/.cache"
os.makedirs(cache_dir, exist_ok=True)

print("Downloading sentence-transformers model: all-MiniLM-L6-v2")

# Download tokenizer and model to cache
tokenizer = AutoTokenizer.from_pretrained(
    'sentence-transformers/all-MiniLM-L6-v2',
    cache_dir=cache_dir
)
model = AutoModel.from_pretrained(
    'sentence-transformers/all-MiniLM-L6-v2',
    cache_dir=cache_dir
)

print("Model downloaded successfully!")
print(f"Cache directory: {cache_dir}")
print(f"Tokenizer: {type(tokenizer)}")
print(f"Model: {type(model)}")
