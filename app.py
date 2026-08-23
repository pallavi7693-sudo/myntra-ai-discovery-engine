import sys
import os
import json
import pandas as pd
import streamlit as st

# Add Scripts directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "Scripts"))

from insights_synthesis_engine import GroundedSynthesisEngine
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
    .badge-positive { background-color: #2E7D32; color: white; }
    .badge-negative { background-color: #C62828; color: white; }
    .badge-mixed { background-color: #6A1B9A; color: white; }
    .badge-neutral { background-color: #616161; color: white; }
    
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_dataset():
    path = os.path.join(BASE_DIR, "Processed Data", "myntra_multidimensional_enriched.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    if "sentiment_analysis" not in df.columns:
        from extract_behavioral_dimensions import analyze_sentiment_vader
        df["sentiment_analysis"] = df.apply(
            lambda r: analyze_sentiment_vader(r.get("processed_text_with_context", r.get("raw_text", ""))),
            axis=1
        )
    return df

def main():
    st.title("🛍️ Myntra Consumer Discovery Engine")
    st.caption("AI-Powered Discovery of Wishlist-to-Purchase Friction")
    
    synthesizer, retriever = load_engines()
    df_data = load_dataset()
    
    if "sentiment_analysis" not in df_data.columns:
        from extract_behavioral_dimensions import analyze_sentiment_vader
        df_data["sentiment_analysis"] = df_data.apply(
            lambda r: analyze_sentiment_vader(r.get("processed_text_with_context", r.get("raw_text", ""))),
            axis=1
        )
    
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
        
        st.divider()
        st.subheader("😊 Consumer Sentiment & Barrier Emotion Analytics (VADER Offline NLP)")
        st.markdown("Quantified sentiment analysis calculated deterministically using offline VADER NLP across consumer touchpoints (No LLM API required).")
        
        quant_json_path = os.path.join(BASE_DIR, "Processed Data", "quantification_results.json")
        if os.path.exists(quant_json_path):
            with open(quant_json_path, "r", encoding="utf-8") as qf:
                qdata = json.load(qf)
            
            sent_summary = qdata.get("sentiment_quantification", {})
            overall_sent = sent_summary.get("overall_sentiment_distribution", {})
            
            # Overall Sentiment Metrics Cards
            s1, s2, s3, s4 = st.columns(4)
            pos_m = overall_sent.get("Positive", {})
            neu_m = overall_sent.get("Neutral", {})
            neg_m = overall_sent.get("Negative", {})
            mix_m = overall_sent.get("Mixed", {})
            
            with s1:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#2E7D32;">{pos_m.get("percentage", 0)}%</div><div class="metric-label">Positive Sentiment ({pos_m.get("numerator", 0):,}/{pos_m.get("denominator", 0):,})</div></div>', unsafe_allow_html=True)
            with s2:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#616161;">{neu_m.get("percentage", 0)}%</div><div class="metric-label">Neutral Sentiment ({neu_m.get("numerator", 0):,}/{neu_m.get("denominator", 0):,})</div></div>', unsafe_allow_html=True)
            with s3:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#C62828;">{neg_m.get("percentage", 0)}%</div><div class="metric-label">Negative Sentiment ({neg_m.get("numerator", 0):,}/{neg_m.get("denominator", 0):,})</div></div>', unsafe_allow_html=True)
            with s4:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#6A1B9A;">{mix_m.get("percentage", 0)}%</div><div class="metric-label">Mixed Sentiment ({mix_m.get("numerator", 0):,}/{mix_m.get("denominator", 0):,})</div></div>', unsafe_allow_html=True)
                
            st.write("")
            st.subheader("Sentiment Distribution by Major Purchase Barrier Category")
            
            barrier_sent_data = sent_summary.get("barrier_sentiment_breakdown", {})
            barrier_rows = []
            for b_name, b_info in barrier_sent_data.items():
                dist = b_info.get("distribution", {})
                barrier_rows.append({
                    "Purchase Barrier": b_name.replace("_", " ").title(),
                    "Total Barrier Records": b_info.get("total_barrier_records", 0),
                    "Usable Denominator": b_info.get("usable_denominator", 0),
                    "Positive (%)": dist.get("Positive", {}).get("percentage", 0.0),
                    "Negative (%)": dist.get("Negative", {}).get("percentage", 0.0),
                    "Neutral (%)": dist.get("Neutral", {}).get("percentage", 0.0),
                    "Mixed (%)": dist.get("Mixed", {}).get("percentage", 0.0)
                })
            df_barrier_sent = pd.DataFrame(barrier_rows)
            st.dataframe(df_barrier_sent, width="stretch")
            
            st.write("")
            st.subheader("Representative Consumer Quotes by Sentiment & Barrier Combination")
            
            col_sel_sent, col_sel_barr = st.columns(2)
            with col_sel_sent:
                sel_sent_val = st.selectbox("Select Sentiment Filter:", ["Negative", "Positive", "Mixed", "Neutral"])
            with col_sel_barr:
                sel_barr_val = st.selectbox("Select Purchase Barrier Filter:", ["price", "quality_uncertainty", "delivery_concern", "return_concern", "size_uncertainty"])
                
            matched_quotes = df_data[
                (df_data["sentiment_analysis"].apply(lambda s: s.get("sentiment_label") == sel_sent_val if isinstance(s, dict) else False)) &
                (df_data["analytical_dimensions"].apply(lambda d: sel_barr_val in d.get("purchase_barriers", [])))
            ]
            
            st.caption(f"Found {len(matched_quotes)} consumer quotes matching {sel_sent_val} Sentiment + {sel_barr_val.replace('_', ' ').title()} Barrier.")
            
            for idx, r_row in matched_quotes.head(4).iterrows():
                s_lbl = r_row.get("sentiment_analysis", {}).get("sentiment_label", "Neutral")
                s_score = r_row.get("sentiment_analysis", {}).get("sentiment_score", 0.0)
                b_class = f"badge-{s_lbl.lower()}"
                
                st.markdown(f"""
                    <div class="evidence-card">
                        <span class="badge {b_class}">{s_lbl} ({s_score})</span>
                        <strong>Channel:</strong> {r_row['source_channel'].upper()} | <strong>Brand:</strong> {r_row['platform_brand'].title()} | <strong>Intent:</strong> <span style="color:#FF3F6C; font-weight:700;">{r_row['primary_intent']}</span><br/>
                        <div style="margin-top:8px; font-style:italic; color:#535766;">"{r_row['raw_text']}"</div>
                    </div>
                """, unsafe_allow_html=True)
                
        st.divider()
        st.subheader("💡 Ranked Unmet Consumer Needs (Cross-Dataset Discovery)")
        st.markdown("Recurring gaps between **user purchase goals** and **current platform experience** detected deterministically across multi-channel touchpoints.")
        
        unmet_json_path = os.path.join(BASE_DIR, "Processed Data", "unmet_needs_results.json")
        if os.path.exists(unmet_json_path):
            with open(unmet_json_path, "r", encoding="utf-8") as uf:
                unmet_data = json.load(uf)
                
            for need in unmet_data.get("ranked_unmet_needs", []):
                str_color = "#2E7D32" if need["strength"] == "High" else ("#EF6C00" if need["strength"] == "Medium" else "#616161")
                
                with st.expander(f"#{need['rank']} {need['title']} — [{need['strength']} Strength | {need['share_pct']}% Share]", expanded=(need['rank'] <= 2)):
                    st.markdown(f"**Unmet Need Statement**: *\"{need['statement']}\"*")
                    
                    u1, u2, u3, u4 = st.columns(4)
                    with u1:
                        st.metric("Evidence Records", f"{need['evidence_count']:,}", f"{need['share_pct']}% share")
                    with u2:
                        st.metric("Source Coverage", f"{need['unique_datasets_count']} Datasets", f"{need['unique_channels_count']} Channels")
                    with u3:
                        st.metric("Associated Barrier", need['associated_purchase_barrier'])
                    with u4:
                        st.metric("Associated Behavior", "Purchase Postponed")
                        
                    st.markdown(f"**Associated User Outcome**: {need['associated_user_outcome']}")
                    st.markdown("**Representative Verbatim Consumer Evidence:**")
                    
                    for q in need.get("representative_evidence", []):
                        st.markdown(f"""
                            <div style="background:#F9F9FB; border-left:3px solid #FF3F6C; padding:10px; border-radius:6px; margin-bottom:8px; font-style:italic; font-size:13px;">
                                "{q['raw_text']}"<br/>
                                <span style="font-size:11px; color:#6C757D; font-style:normal;">— Source: {q['source_file']} ({q['source_channel'].upper()}) | Sentiment: {q['sentiment_label']}</span>
                            </div>
                        """, unsafe_allow_html=True)
        
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
            
        # 1. Primary subset: Reddit evidence (shown from the start)
        reddit_df = df_data[
            (df_data["source_channel"] == "reddit") &
            (df_data["source_channel"].isin(selected_chan)) &
            (df_data["platform_brand"].isin(selected_brand)) &
            (df_data["primary_intent"].isin(selected_intents)) &
            (df_data["primary_intent"].str.lower() != "other")
        ].copy()
        
        reddit_df["intent_priority"] = reddit_df["primary_intent"].apply(
            lambda x: 0 if str(x).lower() in ["wishlist", "price_drop"] else 1
        )
        reddit_df = reddit_df.sort_values(by="intent_priority")
        
        # 2. Secondary subset: Related evidence from YouTube, Play Store & App Store (shown at the bottom)
        non_reddit_channels = [c for c in selected_chan if c != "reddit"]
        if non_reddit_channels:
            yt_df = df_data[(df_data["source_channel"] == "youtube") & (df_data["platform_brand"].isin(selected_brand))] if "youtube" in non_reddit_channels else pd.DataFrame()
            app_df = df_data[(df_data["source_channel"].isin(["playstore", "appstore"])) & (df_data["platform_brand"].isin(selected_brand))] if any(c in non_reddit_channels for c in ["playstore", "appstore"]) else pd.DataFrame()
            non_reddit_df = pd.concat([yt_df.head(6), app_df.head(6)]).dropna(how='all')
        else:
            non_reddit_df = pd.DataFrame()
            
        # Combine: Reddit first (top 38), then YouTube/App Store/PlayStore for Myntra at the bottom (12)
        if not reddit_df.empty and not non_reddit_df.empty:
            filtered_df = pd.concat([reddit_df.head(38), non_reddit_df])
        elif not reddit_df.empty:
            filtered_df = reddit_df.head(50)
        else:
            filtered_df = non_reddit_df.head(50)
            
        st.info(f"Displaying {len(filtered_df)} records — Reddit evidence listed first, with YouTube & App Store / Play Store evidence attached at the bottom.")
        
        for idx, row in filtered_df.iterrows():
            chan = row["source_channel"]
            badge_class = f"badge-{chan}"
            intent_val = row.get("primary_intent", "N/A")
            segment_val = row.get("user_segment", "General User")
            sent_info = row.get("sentiment_analysis", {})
            s_label = sent_info.get("sentiment_label", "Neutral")
            s_badge_class = f"badge-{s_label.lower()}"
            
            st.markdown(f"""
                <div class="evidence-card">
                    <span class="badge {badge_class}">{chan}</span>
                    <span class="badge {s_badge_class}">{s_label}</span>
                    <strong>Brand:</strong> {row['platform_brand'].title()} | <strong>Intent:</strong> <span style="color:#FF3F6C; font-weight:700;">{intent_val}</span> | <strong>Segment:</strong> {segment_val}<br/>
                    <div style="margin-top:8px; font-style:italic; color:#535766;">"{row['raw_text']}"</div>
                </div>
            """, unsafe_allow_html=True)
            
    # TAB 4: DATASET QUALITY & AUDIT EXPLORER
    with tab4:
        st.subheader("Dataset Quality & Audit Explorer")
        
        audit_json_path = os.path.join(BASE_DIR, "Processed Data", "data_audit_results.json")
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
