# 🛍️ Myntra AI Consumer Discovery & Behavioral Insight Engine

> **Unlocking Wishlist-to-Purchase Conversion Velocity Through Multi-Channel Consumer Intelligence**

---

## 📌 Executive Summary

The **Myntra AI Consumer Discovery Engine** is an enterprise-grade, evidence-grounded analytics and retrieval system designed to analyze consumer friction preventing wishlisted products from converting into completed purchases.

By processing **6,562 consumer records across 14 datasets** spanning 4 major touchpoints (**Reddit, Google Play Store, Apple App Store, and YouTube**), the engine quantifies purchase barriers, ranks high-leverage product opportunity areas, and provides deterministic, grounded business insights.

```
Wishlist Consideration  ───►  Friction Evaluation  ───►  Grounded Insight & Opportunity Matrix
                                (971 Denominator)        (Price, Quality, Size, Returns)
```

---

## 🎯 Key Analytical Findings & Opportunity Rankings

> 💡 **Denominator Scoping Rule**: All wishlist-to-purchase barrier calculations use strictly **Myntra's Friction sub-population (971 records)** as the denominator. Overall friction across all brands or overall dataset size is excluded from the denominator.

### Myntra Purchase Barrier Breakdown (Denominator: 971 Myntra Purchase-Hesitation Records)
1. **Price & Discount Delays**: 349 / 971 (**35.9%**)
2. **Quality & Fabric Uncertainty**: 229 / 971 (**23.6%**)
3. **Delivery Delay Concerns**: 185 / 971 (**19.1%**)
4. **Return Policy Concerns**: 143 / 971 (**14.7%**)
5. **Size Uncertainty**: 96 / 971 (**9.9%**)
6. **Lack of Reviews & Social Proof**: 51 / 971 (**5.3%**)
7. **Product Availability**: 32 / 971 (**3.3%**)
8. **Fit Uncertainty**: 17 / 971 (**1.8%**)
9. **Lack of Purchase Urgency**: 16 / 971 (**1.6%**)

### Ranked Opportunity Area Matrix ($Score = Share \% \times Severity Weight$)
1. **`better_price_visibility`**: Score **32.37** (24.9% share [242/971] | 1.3x weight)
2. **`better_quality_information`**: Score **30.66** (21.9% share [213/971] | 1.4x weight)
3. **`better_return_information`**: Score **19.80** (13.2% share [128/971] | 1.5x weight)
4. **`better_size_guidance`**: Score **8.14** (7.4% share [72/971] | 1.1x weight)
5. **`stronger_social_proof`**: Score **5.76** (4.8% share [47/971] | 1.2x weight)
6. **`better_product_comparison`**: Score **4.30** (4.3% share [42/971] | 1.0x weight)
7. **`better_fit_information`**: Score **1.98** (1.8% share [17/971] | 1.1x weight)
8. **`create_purchase_urgency`**: Score **0.36** (0.3% share [3/971] | 1.2x weight)

---

## 🏗️ Architecture & Pipeline Flow

The system is built on a **12-module decoupled architecture** to maintain strict separation of concerns between data cleaning, signal extraction, vector indexing, quantification, and UI presentation:

```
[Raw Consumer Touchpoints] (Reddit / App Stores / YouTube)
           │
           ▼
[1. Multi-Source Ingestion & Deduplication] ──► (14 Datasets / 6,562 Rows)
           │
           ▼
[2. UNDERSTAND: Intent Labeling, Behavioral Signals & VADER Sentiment]
           │
           ▼
[3. RETRIEVE: Vector Embedding Matrix (6562, 5000) & RAG Engine]
           │
           ▼
[4. QUANTIFY: Denominator-Scoped Metrics & Opportunity Scoring]
           │
           ▼
[5. UNMET NEED DETECTION: Empirical Gap & Source Coverage Analyzer]
           │
           ▼
[6. SYNTHESIS & UI: Interactive Discovery Dashboard] (http://localhost:8501)
```

---

## 📊 Dataset Inventory & Audit Summary

The engine processes 14 audited CSV files across 4 consumer touchpoints:

| Dataset File Name | Source / Channel | Rows | Primary Audit Focus |
| :--- | :--- | :--- | :--- |
| `reddit_myntra_additional_labeled.csv` | Reddit (Myntra) | **428** | Additional Reddit intent labeling & signal extraction |
| `reddit_myntra_labeled.csv` | Reddit (Myntra) | **634** | Primary intent & behavioral tag validation |
| `reddit_myntra_additional_cleaned.csv` | Reddit (Myntra) | **428** | Normalized post & comment context data |
| `reddit_myntra_cleaned.csv` | Reddit (Myntra) | **634** | Text normalization & deduplication |
| `myntra_raw.csv` | Reddit / Web | **1,000** | Raw text consistency & deduplication |
| `myntra_playstore.csv` | Google Play Store | **999** | App review friction & checkout bugs |
| `ajio_playstore.csv` | Google Play Store | **999** | Competitor benchmark: AJIO app experience |
| `nykaa_playstore.csv` | Google Play Store | **999** | Competitor benchmark: Nykaa Play Store reviews |
| `nykaa_appstore.csv` | Apple App Store | **49** | Competitor benchmark: Nykaa iOS reviews |
| `youtube_comments_real.csv` | YouTube Comments | **218** | Social try-on/haul consumer sentiment |
| `youtube_comments_test.csv` | YouTube Comments | **99** | Test comment validation |
| `youtube_comments_filtered.csv` | YouTube Comments | **51** | High-relevance video comment audit |
| `youtube_comments_filtered_real.csv` | YouTube Comments | **20** | Ground truth video review sample |
| **Total Multi-Channel Records** | **4 Channels** | **6,562** | **14 Audited CSV Datasets** |

---

## 💡 Key System Capabilities

1. **Executive Discovery Engine (TED Enquiry)**:
   - Supports 10 predefined TED business enquiry questions.
   - **Dynamic Custom Question Router**: Intelligently categorizes custom user queries (e.g. *"Does people use Myntra wishlist to only save items?"*) to tailor insights.
   - **Missing-Attribute & Off-Topic Safeguards**: Detects out-of-scope requests (e.g., demographic age groups, revenue figures) or off-topic queries, returning polite grounded explanations instead of hallucinated fallbacks.

2. **Grounded RAG Evidence Retriever**:
   - Enforces strict Myntra scoping for friction evidence.
   - Excludes generic `'other'` intent records from evidence output.
   - Prioritizes `wishlist` and `price_drop` consumer evidence quotes.

3. **Myntra Opportunity Matrix**:
   - Interactive ranking chart and score breakdown weighted by frequency and severity.

4. **Multi-Channel Evidence Inspector**:
   - Filter evidence by Source Channel (`Reddit`, `PlayStore`, `AppStore`, `YouTube`), Platform Brand (`Myntra`, `AJIO`, `Nykaa`), and Intent Category.

5. **Dataset Quality & Audit Explorer**:
   - Interactive audit dashboard inspecting labeled intent distributions and file statistics.

6. **Deterministic Offline VADER Sentiment Analysis**:
   - **Methodology**: Uses NLTK VADER (`SentimentIntensityAnalyzer`), a rule-based, deterministic, lightweight NLP approach.
   - **No LLM API Required**: Operates 100% offline without external LLM dependencies.
   - **Pipeline Position**: Integrated directly into the **UNDERSTAND** stage (`extract_behavioral_dimensions.py`).
   - **Score Metric (`sentiment_score`)**: Normalized compound score ranging from `-1.0` (extreme negative) to `+1.0` (extreme positive).
   - **Behavioral Signal Coexistence**: Sentiment operates alongside intent, purchase status, and purchase barriers (e.g. tracking positive sentiment towards product styling alongside price postponement barriers).
   - **No Fabrication Safeguard**: Empty/unusable inputs return `sentiment_label: "Unknown"`, `sentiment_score: None`, and `sentiment_confidence: None` without fabricating values.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.9+ installed on Windows / macOS / Linux.

### 2. Install Required Dependencies
```bash
pip install pandas numpy scikit-learn scipy streamlit
```

### 3. Execution Pipeline Scripts (Optional / Re-building Index)
If modifying underlying data, run the pipeline scripts in order:

```bash
# 1. Clean raw Reddit data
python Scripts/clean_additional_reddit_data.py

# 2. Label primary intents
python Scripts/label_reddit_intents.py

# 3. Extract 7-dimensional behavioral signals
python Scripts/extract_behavioral_dimensions.py

# 4. Build vector embeddings and metadata index
python Scripts/build_vector_index.py

# 5. Run quantification & opportunity engines
python Scripts/quantification_engine.py
python Scripts/opportunity_scoring_engine.py

# 6. Audit dataset integrity
python Scripts/audit_datasets.py
```

### 4. Launch Web Application
Start the Streamlit discovery interface:

```bash
python -m streamlit run app.py
```

Open your browser at: **[http://localhost:8501](http://localhost:8501)**

---

## 📁 Repository Structure

```
Myntra Project/
├── app.py                                # Streamlit Web Application Entry Point
├── README.md                             # Project Documentation
├── Raw Data/                             # Normalized & Cleaned Source CSVs
│   ├── reddit_myntra_additional_cleaned.csv
│   ├── myntra_playstore.csv
│   ├── ajio_playstore.csv
│   └── ... (8 raw datasets)
├── Processed Data/                       # Analytical Artifacts & Stores
│   ├── myntra_multidimensional_enriched.json # Enriched 6,562 Records Store
│   ├── vector_index.json                 # TF-IDF Metadata Store
│   ├── vector_embeddings.npz             # Sparse Vector Embedding Matrix
│   ├── quantification_results.json       # Denominator & Barrier Quantification
│   └── data_audit_results.json           # File Integrity Audit Store
├── Scripts/                              # Modular Engineering Pipeline
│   ├── clean_additional_reddit_data.py   # Context Linker & Deduplicator
│   ├── label_reddit_intents.py           # Intent Classifier
│   ├── extract_behavioral_dimensions.py  # 7-Dimensional Signal Extractor
│   ├── build_vector_index.py             # TF-IDF Embedding Generator
│   ├── hybrid_retrieval_engine.py        # RAG Vector Retrieval Engine
│   ├── quantification_engine.py         # Scoped Quantification Analyzer
│   ├── opportunity_scoring_engine.py     # Weighted Matrix Calculator
│   ├── insights_synthesis_engine.py      # Grounded Business Insight Synthesizer
│   └── audit_datasets.py                 # Data Quality Auditor
└── docs/                                 # Technical Architecture & Audits
    ├── architecture.md                   # Complete Architecture Specification
    └── data_validation_audit_report.md   # Data Audit & Benchmark Report
```

---

## 🛡️ License & Grounding Guarantee

This project enforces strict **Deterministic RAG Grounding**. Every metric, percentage, numerator, and evidence quote rendered in the Discovery Engine is computed directly from empirical consumer touchpoints without non-grounded model hallucinations.
