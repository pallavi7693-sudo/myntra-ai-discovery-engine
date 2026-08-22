import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def build_vector_index():
    json_path = "Processed Data/myntra_multidimensional_enriched.json"
    print("==================================================")
    print("STARTING STAGE 3: VECTOR INDEXING & EMBEDDING PIPELINE")
    print("==================================================\n")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Enriched dataset not found at {json_path}. Run Stage 2 first.")
        
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    total_records = len(records)
    print(f"Loaded {total_records} enriched records for vector indexing.")
    
    # Prepare text corpus
    corpus = [r.get("processed_text_with_context", "") for r in records]
    
    # Vectorize corpus using TF-IDF sublinear scaling for semantic relevance
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=5000,
        stop_words='english'
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    print(f"Generated TF-IDF vector embedding matrix of shape: {tfidf_matrix.shape}")
    
    # Build metadata lookup map
    metadata_records = []
    for idx, r in enumerate(records):
        metadata_records.append({
            "vector_id": idx,
            "record_id": r.get("record_id"),
            "source_file": r.get("source_file"),
            "source_channel": r.get("source_channel"),
            "platform_brand": r.get("platform_brand"),
            "primary_intent": r.get("primary_intent"),
            "user_segment": r.get("user_segment"),
            "analytical_dimensions": r.get("analytical_dimensions", {}),
            "evidence": r.get("evidence", {}),
            "raw_text": r.get("raw_text"),
            "processed_text_with_context": r.get("processed_text_with_context")
        })
        
    index_payload = {
        "dataset_summary": {
            "total_records": total_records,
            "vector_dimensions": tfidf_matrix.shape[1]
        },
        "feature_names": vectorizer.get_feature_names_out().tolist(),
        "idf_weights": vectorizer.idf_.tolist(),
        "metadata_store": metadata_records
    }
    
    # Save index payload
    output_index_path = "Processed Data/vector_index.json"
    with open(output_index_path, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2)
        
    # Save scipy matrix as compressed npz or npy
    npz_path = "Processed Data/vector_embeddings.npz"
    from scipy import sparse
    sparse.save_npz(npz_path, tfidf_matrix)
    
    print("\n==================================================")
    print(f"VECTOR INDEXING COMPLETE: Indexed {total_records} records.")
    print(f"Metadata Store saved to: {output_index_path}")
    print(f"Embeddings Matrix saved to: {npz_path}")
    print("==================================================")
    return output_index_path

if __name__ == "__main__":
    build_vector_index()
