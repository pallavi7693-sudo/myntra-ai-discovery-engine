# Technical Specification: Stage 5 Interactive Web Dashboard

> **Module Target:** Interactive Streamlit Discovery Dashboard  
> **Application File:** `app.py`  
> **Backend Integration:** `Scripts/insights_synthesis_engine.py`, `Scripts/opportunity_scoring_engine.py`, `Scripts/hybrid_retrieval_engine.py`  
> **Design Theme:** Dark Mode with HSL accents, Glassmorphic Cards, and Modern Typography.

---

## 1. Dashboard Structure & Navigation

The dashboard is structured into 4 main navigation tabs:

```
[Header Metrics Banner: 5,706 Records | 1,202 Hesitation Population | 4 Touchpoints | 100% Preserved Intents]
├── Tab 1: Executive Discovery Engine (Section 12 Query & Grounded Synthesis)
├── Tab 2: Weighted Opportunity Matrix & Friction Rankings
├── Tab 3: Multi-Channel Evidence Inspector (Reddit / Play Store / App Store / YouTube)
└── Tab 4: Multi-Dataset Audit & Schema Quality Explorer
```

---

## 2. Tab Specifications

### Tab 1: Executive Discovery Engine
- **Preset Business Questions Dropdown**: Select any of the 10 core questions (e.g. *"What prevents wishlisted products from being purchased?"*, *"Why do users wishlist clothes?"*).
- **Custom Query Input**: Type any custom natural language discovery question.
- **Section 12 Executive Report Renderer**: Displays the full 8-part grounded discovery report complete with exact population denominators and verbatim evidence quotes.

### Tab 2: Weighted Opportunity Matrix
- **Metrics Table**: Displays Opportunity Area, Raw Frequency %, Denominator, Severity Weight, and Weighted Opportunity Score.
- **Visual Chart**: Horizontal bar chart comparing opportunity scores across categories.

### Tab 3: Multi-Channel Evidence Inspector
- **Channel Filters**: Filter evidence snippets by channel (`Reddit`, `Play Store`, `App Store`, `YouTube`).
- **Brand Filters**: Filter by brand (`Myntra`, `AJIO`, `Nykaa`).
- **Evidence Card View**: Displays Record ID, intent label, user segment, and verbatim text quote.

### Tab 4: Multi-Dataset Audit & Quality Explorer
- **Dataset Summary Metrics**: Row counts, header statuses, text length distributions across all 12 CSV files.
- **Intent Label Distribution**: Interactive breakdown of the 634 original `primary_intent` labels from `reddit_myntra_labeled.csv`.

---

## 3. Running the Application

To launch the interactive dashboard locally:

```bash
streamlit run app.py
```
