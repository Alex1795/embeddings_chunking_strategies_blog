# Embeddings Chunking Strategies for Elasticsearch

This repository contains code examples demonstrating chunking strategies for vector search in Elasticsearch. It accompanies an Elasticsearch Labs blog post showing the practical impact of different chunking approaches on search relevance and performance.

## Overview

This project demonstrates how chunking strategies affect search results in Elasticsearch using the `semantic_text` field type with ELSER (Elastic Learned Sparse EncodeR). The demo compares search performance with and without chunking using real Wikipedia data for countries in the Americas.

## What This Demo Shows

- **Chunking vs No Chunking**: Direct comparison of search results with sentence-based chunking versus no chunking
- **Real Data Testing**: Uses Wikipedia articles for 26 countries in the Americas
- **Semantic Search**: Leverages Elasticsearch's `semantic_text` field with ELSER model
- **Visual Comparison**: Color-coded terminal output showing search results side-by-side

## Repository Structure

```
├── set_up.py                    # Index setup and data ingestion
├── run_semantic_search.py       # Search comparison demo
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Scripts

### `set_up.py`
- Creates two inference endpoints with different chunking strategies
- Sets up the `countries_wiki` index with semantic_text mappings
- Downloads and indexes Wikipedia content for 26 American countries

### `run_semantic_search.py`
- Implements semantic search functions for both chunking strategies
- Provides visual comparison of search results
- Includes multiple demo queries to test different scenarios

## Prerequisites

- Python 3.8+
- Elasticsearch deployment (with ELSER model available)
- Environment variables for Elasticsearch connection

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Alex1795/embeddings_chunking_strategies_blog.git
cd embeddings_chunking_strategies_blog
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export ES_HOST="your-elasticsearch-endpoint"
export ES_API_KEY="your-api-key"
```

## Usage

### 1. Set Up the Demo Environment

Run the setup script to create the index and ingest data:

```bash
python set_up.py
```

This script will:
- Create two inference endpoints:
  - `sentence-chunking-demo`: Uses sentence-based chunking (max 80 words, 1 sentence overlap)
  - `none-chunking-demo`: No chunking strategy
- Set up the `countries_wiki` index with semantic_text fields
- Download and index Wikipedia articles for 26 countries

### 2. Run the Search Comparison

Execute the search demo to see chunking strategies in action:

```bash
python run_semantic_search.py
```

The demo will run several test queries and display:
- Search results for both strategies
- Highlighted relevant text chunks
- Search scores and result counts
- Summary comparison tables

## Chunking Strategies Demonstrated

### Sentence Chunking Strategy
- **Strategy**: `sentence`
- **Max Chunk Size**: 80 words
- **Overlap**: 1 sentence
- **Benefits**: Maintains sentence boundaries, provides focused context
- **Use Case**: When you need precise, contextually relevant matches

### No Chunking Strategy  
- **Strategy**: `none`
- **Processing**: Entire document as single unit
- **Benefits**: Preserves full document context
- **Use Case**: When document-level context is more important than precision

## Demo Queries

The repository includes these test queries:
- "countries in the inca empire"
- "coffee production" 
- "oil and petroleum exports"
- "beach destinations"
- "hockey"

You can easily add more queries to test
## Technical Implementation

### Inference Models Setup
```python
# Sentence chunking configuration
sentence_chunking = {
    "task_type": "sparse_embedding",
    "service": "elasticsearch", 
    "service_settings": {
        "model_id": ".elser_model_2_linux-x86_64"
    },
    "chunking_settings": {
        "strategy": "sentence",
        "max_chunk_size": 80,
        "sentence_overlap": 1
    }
}
```
```python
# No chunking configuration
none_chunking = {
    "task_type": "sparse_embedding",
    "service": "elasticsearch", 
    "service_settings": {
        "model_id": ".elser_model_2_linux-x86_64"
    },
    "chunking_settings": {
        "strategy": "none"
    }
}
```
### Index Mapping
```python
"wiki_article": {
    "type": "text",
    "fields": {
        "none": {
            "type": "semantic_text",
            "inference_id": "none-chunking-demo"
        },
        "sentence": {
            "type": "semantic_text", 
            "inference_id": "sentence-chunking-demo"
        }
    }
}
```

### Semantic Search Query
```python
search_body = {
    "query": {
        "semantic": {
            "field": "wiki_article.sentence",  # or "wiki_article.none"
            "query": query
        }
    },
    "highlight": {
        "fields": {
            "wiki_article.sentence": {
                "order": "score",
                "number_of_fragments": 1
            }
        }
    }
}
```

## Key Insights

This demo illustrates several important concepts:

1. **Precision vs Context**: Chunking provides more precise matches but may miss broader context
2. **Query Dependency**: Some queries benefit more from chunking than others
3. **Relevance Scoring**: Chunking can significantly impact relevance scores
4. **Practical Trade-offs**: Choice of strategy depends on specific use case requirements

## Data Source

The demo uses Wikipedia articles for these 26 countries:
- **North America**: United States, Canada, Mexico
- **Central America**: Guatemala, Belize, Honduras, El Salvador, Nicaragua, Costa Rica, Panama
- **Caribbean**: Cuba, Jamaica, Haiti, Dominican Republic, Trinidad and Tobago, Barbados  
- **South America**: Brazil, Argentina, Chile, Peru, Colombia, Venezuela, Ecuador, Bolivia, Paraguay, Uruguay

## Configuration Options

The demo is configured for optimal demonstration purposes:

- **Chunk Size**: 80 words (suitable for sentence-based chunking)
- **Overlap**: 1 sentence (prevents context loss at boundaries)
- **Model**: ELSER v2 (Elasticsearch's sparse embedding model)
- **Timeout**: 600 seconds (accommodates model inference time)

## Performance Considerations

- **Setup Time**: Initial setup may take several minutes due to Wikipedia downloads and indexing
- **Model Loading**: First queries may be slower as ELSER model loads
- **Memory Usage**: ELSER requires sufficient ML node resources
- **Index Size**: Full Wikipedia articles create substantial index size

## Troubleshooting

Common issues and solutions:

- **Model Not Available**: Ensure ELSER model is deployed on your cluster
- **Timeout Errors**: Increase timeout values for large document processing
- **Memory Issues**: Ensure adequate ML node resources
- **API Key Permissions**: Verify API key has necessary cluster and index permissions



**Note**: This repository demonstrates chunking strategies for educational purposes. For production implementations, consider additional factors such as document types, query patterns, and performance requirements.