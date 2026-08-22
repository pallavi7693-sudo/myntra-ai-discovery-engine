import sys
import os
import json
import pandas as pd
import streamlit as st

# Add Scripts directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "Scripts"))

from llm_synthesis_engine import GroundedSynthesisEngine
from opportunity_scoring_engine import compute_opportunity_matrix
from hybrid_retrieval_engine import HybridRetrievalEngine

# Set Page Config
st.set_page_config(
    page_title="Myntra Consumer Discovery Engine",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Myntra Light Theme & Brand Palette)
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F6;
        color: #282C3F;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .stApp {
        background-color: #F5F5F6;
    }
    
    h1, h2, h3 {
        color: #282C3F !important;
        font-weight: 700 !important;
    }
    
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEC;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(40, 44, 63, 0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 63, 108, 0.12);
        border-color: #FF3F6C;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #FF3F6C;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        color: #535766;
        margin-top: 6px;
    }
    
    .report-box {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEC;
        border-left: 5px solid #FF3F6C;
        border-radius: 10px;
        padding: 28px;
        margin-top: 15px;
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        color: #282C3F;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }
    
    .evidence-card {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEC;
        border-left: 4px solid #FF3F6C;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 8px;
        text-transform: uppercase;
    }
    .badge-reddit { background-color: #FF4500; color: white; }
    .badge-playstore { background-color: #00875A; color: white; }
    .badge-appstore { background-color: #0066CC; color: white; }
    .badge-youtube { background-color: #FF0000; color: white; }
    
    .stButton>button {
        background-color: #FF3F6C !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 12px rgba(255, 63, 108, 0.25) !important;
    }
    .stButton>button:hover {
        background-color: #E0355D !important;
        box-shadow: 0 6px 16px rgba(255, 63, 108, 0.35) !important;
    }
    
    .stSelectbox>div>div, .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        color: #282C3F !important;
        border: 1px solid #D4D5D9 !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

def load_engines():
    synthesizer = GroundedSynthesisEngine()
    retriever = HybridRetrievalEngine()
    return synthesizer, retriever

@st.cache_data
def load_dataset():
    path = "Processed Data/myntra_multidimensional_enriched.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def main():
    st.title("🛍️ Myntra Consumer Discovery Engine")
    st.caption("AI-Powered Consumer Behavioral Insight & Purchase Friction Analytics")
    
    synthesizer, retriever = load_engines()
    df_data = load_dataset()
    
    total_records = len(df_data)
    myntra_friction_df = df_data[(df_data["platform_brand"] == "myntra") & (df_data.apply(lambda r: len(r['analytical_dimensions']['purchase_barriers']) > 0 or r['analytical_dimensions']['purchase_status'] == 'postponed', axis=1))]
    myntra_friction_count = len(myntra_friction_df)
    
    # Top Banner Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_records:,}</div><div class="metric-label">Total Multi-Channel Records</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{myntra_friction_count:,}</div><div class="metric-label">Myntra Friction Sub-Population</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">Myntra-Only</div><div class="metric-label">Friction & Barrier Scope</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">Cross-Platform</div><div class="metric-label">Wishlist Intent Scope</div></div>', unsafe_allow_html=True)
        
    st.write("")
    st.divider()
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Executive Discovery Engine (TED Enquiry)",
        "📊 Myntra Opportunity Matrix & Friction",
        "💬 Multi-Channel Evidence Inspector",
        "📂 Dataset Quality & Audit Explorer"
    ])
    
    # TAB 1: EXECUTIVE DISCOVERY ENGINE (TED ENQUIRY)
    with tab1:
        st.subheader("Executive Discovery Engine (TED Enquiry)")
        st.markdown("Select any of the **10 mandatory TED enquiry business questions** below:")
        
        ted_questions = [
            "Why do users add fashion products to their wishlist?",
            "What prevents wishlisted products from eventually being purchased?",
            "What uncertainties remain after users have identified a product they like?",
            "What causes users to postpone a purchase?",
            "How do users compare multiple shortlisted products?",
            "What information do users seek outside Myntra/AJIO before purchasing?",
            "What role do fit, size, styling, price, reviews, occasion and social validation play?",
            "When do users use the wishlist as genuine purchase intent versus simply as a bookmarking mechanism?",
            "How do these behaviors differ across user segments?",
            "What unmet needs emerge consistently across user conversations?"
        ]
        
        selected_preset = st.selectbox("Select a TED Enquiry Question:", ["-- Custom Question --"] + ted_questions)
        
        if selected_preset != "-- Custom Question --":
            query_input = selected_preset
        else:
            query_input = st.text_input("Or enter your custom discovery question:", "What prevents wishlisted products from eventually being purchased?")
            
        if st.button("🚀 Generate Grounded Executive Report"):
            with st.spinner("Executing hybrid retrieval, Myntra-scoped quantification, and grounded synthesis..."):
                report_md = synthesizer.generate_executive_report(query_input)
                
            st.success("Myntra Executive Discovery Report Generated Successfully!")
            
            # Render Report Output Box
            st.markdown(f'<div class="report-box">{report_md}</div>', unsafe_allow_html=True)
            
            st.write("")
            st.download_button(
                label="📥 Download Executive Report (.md)",
                data=report_md,
                file_name="myntra_executive_discovery_report.md",
                mime="text/markdown"
            )
            
    # TAB 2: MYNTRA OPPORTUNITY MATRIX
    with tab2:
        st.subheader("Myntra-Scoped Opportunity Area Rankings")
        st.markdown("Friction opportunities analyzed **strictly on Myntra customer feedback** (Denominator: 969 records) ranked by **Frequency (%) × Friction Severity Weight**.")
        
        opp_matrix = compute_opportunity_matrix()
        df_opp = pd.DataFrame(opp_matrix)
        
        st.dataframe(
            df_opp[["opportunity_area", "opportunity_score", "severity_weight", "raw_frequency_pct", "numerator", "denominator", "population_name"]],
            column_config={
                "opportunity_area": "Opportunity Area",
                "opportunity_score": st.column_config.NumberColumn("Weighted Score", format="%.2f"),
                "severity_weight": st.column_config.NumberColumn("Severity Weight", format="%.1fx"),
                "raw_frequency_pct": st.column_config.NumberColumn("Myntra Share (%)", format="%.1f%%"),
                "numerator": "Myntra Records",
                "denominator": "Myntra Denominator",
                "population_name": "Population Scope"
            },
            width="stretch"
        )
        
        st.subheader("Myntra Opportunity Score Chart")
        st.bar_chart(df_opp.set_index("opportunity_area")["opportunity_score"])
        
    # TAB 3: MULTI-CHANNEL EVIDENCE INSPECTOR
    with tab3:
        st.subheader("Multi-Channel Evidence Inspector")
        st.markdown("Inspect verbatim consumer quotes across Reddit, Google Play Store, Apple App Store, and YouTube Comments focused on **Wishlist & Price-Drop evidence**.")
        
        col_chan, col_brand, col_intent = st.columns(3)
        with col_chan:
            selected_chan = st.multiselect("Filter by Source Channel:", ["reddit", "playstore", "appstore", "youtube"], default=["reddit", "playstore", "appstore", "youtube"])
        with col_brand:
            selected_brand = st.multiselect("Filter by Platform Brand:", ["myntra", "ajio", "nykaa"], default=["myntra", "ajio", "nykaa"])
            
        all_intents = sorted([str(i) for i in df_data["primary_intent"].unique() if str(i).lower() != "other"])
        default_intents = [i for i in ["wishlist", "price_drop", "product_research", "purchase_intent"] if i in all_intents]
        if not default_intents:
            default_intents = all_intents
            
        with col_intent:
            selected_intents = st.multiselect("Filter by Primary Intent (Excludes 'Other'):", all_intents, default=default_intents)
            
        # Filter out 'other' intent and apply channel, brand, and intent selections
        filtered_df = df_data[
            (df_data["source_channel"].isin(selected_chan)) &
            (df_data["platform_brand"].isin(selected_brand)) &
            (df_data["primary_intent"].isin(selected_intents)) &
            (df_data["primary_intent"].str.lower() != "other")
        ].copy()
        
        # Priority sorting: wishlist and price_drop first
        filtered_df["intent_priority"] = filtered_df["primary_intent"].apply(
            lambda x: 0 if str(x).lower() in ["wishlist", "price_drop"] else 1
        )
        filtered_df = filtered_df.sort_values(by="intent_priority")
        
        st.info(f"Displaying {min(50, len(filtered_df))} high-relevance evidence records (Wishlist / Price-Drop focused, 'Other' excluded) out of {len(filtered_df)} matching records.")
        
        for idx, row in filtered_df.head(50).iterrows():
            chan = row["source_channel"]
            badge_class = f"badge-{chan}"
            
            st.markdown(f"""
                <div class="evidence-card">
                    <span class="badge {badge_class}">{chan}</span>
                    <strong>Brand:</strong> {row['platform_brand'].title()} | <strong>Intent:</strong> <span style="color:#FF3F6C; font-weight:700;">{row['primary_intent']}</span> | <strong>Segment:</strong> {row['user_segment']}<br/>
                    <div style="margin-top:8px; font-style:italic; color:#535766;">"{row['raw_text']}"</div>
                </div>
            """, unsafe_allow_html=True)
            
    # TAB 4: DATASET QUALITY & AUDIT EXPLORER
    with tab4:
        st.subheader("Dataset Quality & Audit Explorer")
        
        audit_json_path = "Processed Data/data_audit_results.json"
        if os.path.exists(audit_json_path):
            with open(audit_json_path, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
                
            total_files_count = audit_data.get("summary", {}).get("total_files", 14)
            total_rows_count = audit_data.get("summary", {}).get("total_rows", 6562)
            
            st.markdown(f"Overview of the **{total_files_count} CSV datasets ({total_rows_count:,} rows)** across multi-channel touchpoints.")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{total_files_count} Datasets</div><div class="metric-label">Audited CSV Files</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{total_rows_count:,}</div><div class="metric-label">Total Audited Rows</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown('<div class="metric-card"><div class="metric-value">4 Channels</div><div class="metric-label">Reddit, PlayStore, AppStore, YouTube</div></div>', unsafe_allow_html=True)
                
            st.write("")
            st.subheader("Labeled Intent Distribution Across Reddit Datasets")
            
            lbl_files = ["reddit_myntra_labeled.csv", "reddit_myntra_additional_labeled.csv"]
            selected_lbl = st.selectbox("Select Labeled Dataset:", lbl_files)
            
            labeled_info = audit_data["datasets"].get(selected_lbl, {}).get("labeled_intent_distribution", {})
            if labeled_info:
                df_intent = pd.DataFrame([{"Intent": k, "Count": v["count"], "Share (%)": v["share_pct"]} for k, v in labeled_info.items()])
                st.dataframe(df_intent, width="stretch")
                st.bar_chart(df_intent.set_index("Intent")["Count"])

if __name__ == "__main__":
    main()
