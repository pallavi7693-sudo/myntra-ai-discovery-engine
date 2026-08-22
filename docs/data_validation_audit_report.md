# Data Validation & Label-Quality Audit Report

> **Project Target:** Myntra Wishlist-to-Purchase Journey Analysis  
> **Audit Date:** August 2026  
> **Scope:** Comprehensive audit of **14 CSV Datasets (6,562 Total Rows)** across `Raw Data/` and `Processed Data/`

---

## 1. Executive Summary

This audit evaluates the data quality, schema integrity, duplicate rates, and label distribution across all 14 CSV files in the workspace. The primary goal is to determine whether the existing labeled and raw datasets can support the business objective: **identifying, quantifying, and comparing friction factors preventing wishlisted products from being purchased on Myntra**.

### Key Audit Findings
1. **Single-Intent Label Loss & Dataset Expansion:**  
   In the original labeled dataset (`reddit_myntra_labeled.csv`), **47.16% (299 out of 634 rows)** were categorized under `other`. With the integration of `reddit_myntra_additional_labeled.csv` (428 rows), an additional **29 wishlist intent records** were added, expanding total Reddit discussions to **1,062 posts/comments**.
2. **Multi-Touchpoint Reach:**  
   The workspace contains rich data across 4 distinct consumer touchpoints:
   - **Reddit Discussions** (1,062 posts/comments across 4 datasets, avg. length **589.8 - 770.5 characters**) - *High depth for behavioral signals*.
   - **Play Store App Reviews** (Myntra, AJIO, Nykaa: ~3,000 reviews) - *High volume for app friction & UI bugs*.
   - **iOS App Store Reviews** (Nykaa: 50 reviews) - *iOS competitor benchmark*.
   - **YouTube Comments** (388 comments across 4 files) - *Social try-on haul sentiment & fit feedback*.
3. **Header Schema Discrepancies:**  
   Raw Play Store and App Store CSV files (`myntra_playstore.csv`, `ajio_playstore.csv`, `nykaa_playstore.csv`, `nykaa_appstore.csv`) do not contain header rows. The first row contains review data. Data ingestion pipelines must explicitly specify `header=None`.
4. **Data Redundancy & Empty Files:**  
   - `reddit_myntra_raw.csv` is currently empty (0 rows, schema placeholder).
   - High duplicate text rates occur in Play Store reviews due to single-word reviews (e.g. "Great.", "Bad").

---

## 2. Multi-Dataset Inventory & Audit Summary

| Dataset File | Directory | Source Channel | Rows | Cols | Header Status | Valid Text | Dup Rate | Avg Char Len | Primary Audit Focus |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `reddit_myntra_additional_labeled.csv` | `Processed Data/` | Reddit (Myntra) | **428** | 17 | Headered | 428 (100%) | 1.40% | 589.8 | Additional Reddit intent labeling |
| `reddit_myntra_labeled.csv` | `Processed Data/` | Reddit (Myntra) | **634** | 17 | Headered | 634 (100%) | 2.21% | 770.5 | Intent label quality & distribution |
| `reddit_myntra_additional_cleaned.csv` | `Raw Data/` | Reddit (Myntra) | **428** | 13 | Headered | 428 (100%) | 1.40% | 589.8 | Cleaned additional Reddit dataset |
| `reddit_myntra_cleaned.csv` | `Raw Data/` | Reddit (Myntra) | **634** | 13 | Headered | 634 (100%) | 2.21% | 770.5 | Data cleaning & text normalization |
| `myntra_raw.csv` | `Raw Data/` | Reddit / Web | **1,000** | 8 | Headered | 1,000 (100%) | 0.50% | 36.0 | Raw text completeness |
| `reddit_myntra_raw.csv` | `Raw Data/` | Reddit | **0** | 8 | Headered | 0 (0%) | 0.00% | 0.0 | Placeholder schema |
| `myntra_playstore.csv` | `Raw Data/` | Google Play Store | **1,000** | 10 | Headerless | 1,000 (100%) | 27.10% | 51.7 | Myntra App UI & wishlist friction |
| `ajio_playstore.csv` | `Raw Data/` | Google Play Store | **1,000** | 10 | Headerless | 1,000 (100%) | 39.80% | 56.1 | Competitor benchmark (AJIO) |
| `nykaa_playstore.csv` | `Raw Data/` | Google Play Store | **1,000** | 10 | Headerless | 1,000 (100%) | 29.00% | 92.5 | Competitor benchmark (Nykaa) |
| `nykaa_appstore.csv` | `Raw Data/` | Apple App Store | **50** | 9 | Headerless | 50 (100%) | 98.00% | 23.0 | Competitor benchmark (iOS) |
| `youtube_comments_real.csv` | `Raw Data/` | YouTube Comments | **218** | 5 | Headered | 218 (100%) | 0.92% | 44.3 | Social video haul try-on feedback |
| `youtube_comments_test.csv` | `Raw Data/` | YouTube Comments | **99** | 5 | Headered | 99 (100%) | 9.09% | 47.1 | Spam / test filtering |
| `youtube_comments_filtered.csv` | `Raw Data/` | YouTube Comments | **51** | 7 | Headered | 51 (100%) | 15.69% | 46.5 | Keyword-filtered comments |
| `youtube_comments_filtered_real.csv` | `Raw Data/` | YouTube Comments | **20** | 7 | Headered | 20 (100%) | 0.00% | 87.6 | High-signal real haul sample |

---

## 3. Deep-Dive Audit: Labeled Dataset (`reddit_myntra_labeled.csv`)

### Single-Intent Distribution Analysis (634 Rows)

```
Intent Class           Count    Share (%)   Visual Share
-------------------------------------------------------------------------
other                  299      47.16%      ████████████████████████
customer_service       102      16.09%      ████████
delivery                62       9.78%      █████
product_quality         59       9.31%      █████
coupon                  33       5.21%      ███
cancellation_refund     31       4.89%      ██
price_drop              24       3.79%      ██
wishlist                10       1.58%      █
restock_availability     6       0.95%      ▏
purchase_intent          4       0.63%      ▏
sale_discount            3       0.47%      ▏
product_discovery        1       0.16%      ▏
```

### Critical Problem Identified: "The Single-Intent Bottleneck"
- **47.16% classified as `other`:** Because the single-intent classifier attempts to pick one primary label, complex discussions containing multiple topics (e.g., *"Loved this jacket on Myntra wishlist, but waiting for sales and unsure about size M fit"*) get dumped into `other` or arbitrarily forced into `product_quality` or `customer_service`.
- **Wishlist Under-representation:** Only **10 posts (1.58%)** are labeled `wishlist`, giving a false impression that wishlist discussions are rare. In reality, wishlist intent occurs alongside price waiting, fit uncertainty, and review seeking.

---

## 4. Assessment Against the 10 Business Questions

| # | Business Question | Can Current Single-Intent Data Answer It? | Multi-Dimensional Schema Requirement |
| :--- | :--- | :--- | :--- |
| **1** | Why do users wishlist products? | ❌ No (Only 10 `wishlist` rows) | Requires `user_behavior` + `information_needs` multi-tagging |
| **2** | What prevents wishlisted items from purchase? | ❌ No (Barriers hidden in `other` & `product_quality`) | Requires `purchase_barriers` tag (size, fit, price, reviews) |
| **3** | What uncertainties remain after shortlisting? | ❌ No | Requires `purchase_barriers` & `decision_factors` |
| **4** | What causes users to postpone purchases? | ⚠️ Partial (24 `price_drop` rows) | Requires `purchase_status: postponed` & delay triggers |
| **5** | How do users compare shortlisted products? | ❌ No (0 comparison tags) | Requires `user_behavior: product_comparison` |
| **6** | What info do users seek outside Myntra/AJIO? | ⚠️ Partial (Reddit discussions) | Requires `information_needs` tag across Reddit & YouTube |
| **7** | Role of fit, size, price, quality, reviews? | ⚠️ Partial (Single intent forces 1 factor) | Requires multi-factor array (`decision_factors`) |
| **8** | When is wishlist intent genuine vs bookmarking? | ❌ No | Requires `purchase_stage` + `purchase_status` tracking |
| **9** | How do behaviors differ across user segments? | ❌ No (No segment metadata) | Requires `user_segment` classification pipeline |
| **10** | What unmet needs emerge across conversations? | ❌ No (No opportunity mapping) | Requires `opportunity_area` multi-label extraction |

---

## 5. Architectural Recommendations & Proposed Extraction Schema

To resolve these limitations, we recommend advancing to **Stage 2: Multi-Dimensional Behavioral Extraction**.

### Recommended Unified Extraction Schema

```json
{
  "record_id": "string",
  "source_channel": "reddit | playstore | appstore | youtube",
  "platform_brand": "myntra | ajio | nykaa",
  "raw_text": "string",
  "user_segment": "price_sensitive | fit_hesitant | research_heavy | impulse_buyer",
  "primary_intent": "original_intent_preserved",
  "multi_dimensions": {
    "user_behavior": ["wishlist", "purchase_postponed", "product_research"],
    "purchase_stage": "consideration",
    "purchase_status": "postponed",
    "purchase_barriers": ["size_uncertainty", "lack_of_reviews"],
    "information_needs": ["reviews", "fit_information"],
    "decision_factors": ["fit", "size", "price"],
    "opportunity_area": "better_size_guidance"
  }
}
```

### Action Plan
1. **Preserve existing labeled dataset** (`reddit_myntra_labeled.csv`) — do NOT discard or rewrite raw intent.
2. **Implement Header Normalizer** for Play Store / App Store CSVs during multi-channel ingestion.
3. **Build Multi-Dimensional Extractor** (Stage 2) to enrich all 5,706 records across the 7 dimensions.
