"""Streamlit Web Application for AI-Powered Personalized Outfit Recommendation System.

Provides 6 integrated sections:
1. Home
2. Body & Skin Analysis
3. My Profile
4. Outfit Recommendations
5. History
6. Model Evaluation
"""

import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

import config
from backend.body_shape_analysis import analyze_body_shape
from backend.dataset_loader import load_catalogue
from backend.gbm_recommender import (
    load_model,
    predict_preferred_category,
    report_evaluation_metrics,
    return_prediction_results,
    train_model,
)
from backend.profile_manager import ProfileManager
from backend.recommendation_engine import HybridRecommendationEngine
from backend.skin_tone_analysis import analyze_skin_tone

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Skin Tone Body Measurement Based Dress Recommendation",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-primary { background: #3b82f6; color: white; }
    .badge-success { background: #10b981; color: white; }
    .badge-warning { background: #f59e0b; color: black; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_hybrid_engine():
    """Caches recommendation engine instance for fast multi-modal inference."""
    return HybridRecommendationEngine()


@st.cache_resource
def get_profile_manager():
    """Initializes SQLite profile manager."""
    return ProfileManager()


# Initialize Session State
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "user_default"
if "uploaded_image_bgr" not in st.session_state:
    st.session_state["uploaded_image_bgr"] = None
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None
if "selected_page" not in st.session_state:
    st.session_state["selected_page"] = "Home"

engine = get_hybrid_engine()
pm = get_profile_manager()

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 👗 **Fashion AI Engine**")
    user_row = pm.get_or_create_user(st.session_state["user_id"])
    st.caption(f"Active Profile: **{user_row['display_name']}** (`{user_row['user_id']}`)")

    st.markdown("### 🧭 **Navigation**")
    nav_options = [
        "🏠 Home",
        "🔍 Body & Skin Analysis",
        "👤 My Profile",
        "👗 Outfit Recommendations",
        "📜 History",
    ]
    page_lookup = {
        "🏠 Home": "Home",
        "🔍 Body & Skin Analysis": "Body & Skin Analysis",
        "👤 My Profile": "My Profile",
        "👗 Outfit Recommendations": "Outfit Recommendations",
        "📜 History": "History",
    }
    reverse_lookup = {v: k for k, v in page_lookup.items()}

    current_nav = reverse_lookup.get(st.session_state.get("selected_page", "Home"), "🏠 Home")
    selected_nav = st.radio(
        "Select Module",
        nav_options,
        index=nav_options.index(current_nav) if current_nav in nav_options else 0,
        label_visibility="collapsed",
    )
    page = page_lookup[selected_nav]
    st.session_state["selected_page"] = page

    st.markdown("---")
    with st.expander("⚙️ **Quick Config (Hybrid Weights)**", expanded=True):
        st.caption("Adjust multi-modal ranking priorities:")
        w_tfidf = st.slider("📝 Text (TF-IDF)", 0.0, 1.0, config.DEFAULT_WEIGHTS["tfidf"], 0.05)
        w_clip = st.slider("🖼️ Visual (CLIP)", 0.0, 1.0, config.DEFAULT_WEIGHTS["clip"], 0.05)
        w_gbm = st.slider("🧠 ML Category (GBM)", 0.0, 1.0, config.DEFAULT_WEIGHTS["gbm"], 0.05)
        w_attr = st.slider("👤 Profile Compatibility", 0.0, 1.0, config.DEFAULT_WEIGHTS["attributes"], 0.05)

    custom_weights = {
        "tfidf": w_tfidf,
        "clip": w_clip,
        "gbm": w_gbm,
        "attributes": w_attr,
    }


# ==============================================================================
# PAGE 1: HOME
# ==============================================================================
if page == "Home":
    st.markdown('<div class="main-title">Skin Tone Body Measurement Based Dress Recommendation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Personalized fashion guidance combining computer vision, natural language search, and Gradient Boosting intelligence.</div>', unsafe_allow_html=True)

    col_hero1, col_hero2 = st.columns([3, 2])

    with col_hero1:
        st.markdown("""
        ### 🚀 How the System Works
        1. **📸 Visual Intelligence (OpenCV & MoveNet):** Analyzes uploaded full-body photograph to detect skin undertones and estimate silhouette body proportions.
        2. **🧠 Predictive Machine Learning (Gradient Boosting):** Evaluates physical and style parameters to forecast high-affinity clothing categories.
        3. **🔍 Semantic Matching (TF-IDF & Cosine Similarity):** Searches a rich clothing catalog against style keywords, occasion demands, and budget constraints.
        4. **🖼️ Deep Visual Harmony (CLIP):** Compares photo embeddings with apparel cards for complementary aesthetic discovery.
        """)

        st.info("💡 **Tip:** Upload a clear full-body photo below, or head straight to **Outfit Recommendations** to explore by text preference.")

        uploaded_file = st.file_uploader(
            "Upload Full-Body Photograph (JPG, PNG, JPEG)",
            type=["jpg", "png", "jpeg"],
            help="Your photo is processed locally in memory for proportion and skin tone extraction. Photos are NOT saved permanently.",
        )

        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            nparr = np.frombuffer(bytes_data, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img_bgr is not None:
                st.session_state["uploaded_image_bgr"] = img_bgr
                st.success("✅ Image loaded successfully!")

                if st.button("✨ Run Body & Skin Analysis Now", use_container_width=True):
                    with st.spinner("Executing Computer Vision pipelines..."):
                        skin_res = analyze_skin_tone(img_bgr)
                        body_res = analyze_body_shape(img_bgr)
                        st.session_state["analysis_results"] = {
                            "skin": skin_res,
                            "body": body_res,
                        }
                    st.session_state["selected_page"] = "Body & Skin Analysis"
                    st.rerun()

    with col_hero2:
        if st.session_state["uploaded_image_bgr"] is not None:
            st.image(
                cv2.cvtColor(st.session_state["uploaded_image_bgr"], cv2.COLOR_BGR2RGB),
                caption="Current Active Image",
                use_container_width=True,
            )
        else:
            st.image(
                "outfits/formal_navy_wool_suit.jpg" if os.path.exists("outfits/formal_navy_wool_suit.jpg") else "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600",
                caption="Multi-Modal Style Engine",
                use_container_width=True,
            )


# ==============================================================================
# PAGE 2: BODY AND SKIN ANALYSIS
# ==============================================================================
elif page == "Body & Skin Analysis":
    st.markdown('<div class="main-title">Body Proportion & Skin Tone Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Computer vision analysis of anatomical silhouettes and skin undertones.</div>', unsafe_allow_html=True)

    img_bgr = st.session_state.get("uploaded_image_bgr")

    if img_bgr is None:
        st.warning("⚠️ No photograph currently loaded. Please upload a photo on the Home page or below.")
        new_file = st.file_uploader("Upload Photograph", type=["jpg", "png", "jpeg"], key="p2_uploader")
        if new_file:
            nparr = np.frombuffer(new_file.read(), np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            st.session_state["uploaded_image_bgr"] = img_bgr
            st.rerun()
    else:
        # Run or retrieve analysis
        if st.session_state.get("analysis_results") is None:
            with st.spinner("Analyzing image..."):
                skin_res = analyze_skin_tone(img_bgr)
                body_res = analyze_body_shape(img_bgr)
                st.session_state["analysis_results"] = {"skin": skin_res, "body": body_res}

        skin_res = st.session_state["analysis_results"]["skin"]
        body_res = st.session_state["analysis_results"]["body"]

        col_img, col_metrics = st.columns([1, 1])

        with col_img:
            st.image(
                cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
                caption="Analyzed Photograph",
                use_container_width=True,
            )
            st.caption("ℹ️ *Image-based analyses are non-intrusive geometric estimations.*")

        with col_metrics:
            st.subheader("👤 Profile Extraction Results")

            # Skin Tone Cards
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Estimated Skin Tone", skin_res.get("skin_tone", "Unknown"))
            with c2:
                st.metric("Estimated Undertone", skin_res.get("undertone", "Unknown"))

            # Body Shape Cards
            c3, c4 = st.columns(2)
            with c3:
                st.metric("Estimated Body Shape", body_res.get("body_shape", "Unknown"))
            with c4:
                st.metric("Shoulder/Hip Ratio", f"{body_res.get('shoulder_hip_ratio', 1.0):.2f}")

            st.caption(f"Analysis Method: `{body_res.get('method', 'Automatic')}`")

            # Diagnostic warnings
            if skin_res.get("confidence_warning"):
                st.warning(f"⚠️ Skin Tone Note: {skin_res['confidence_warning']}")
            if body_res.get("warning"):
                st.warning(f"⚠️ Body Shape Note: {body_res['warning']}")

            st.info(body_res.get("disclaimer", "Estimates represent visual proportions, not certified dimensions."))

        st.markdown("---")
        st.subheader("✏️ Manual Correction / Confirmation")
        st.write("If lighting conditions or pose affected the detection, adjust below:")

        col_corr1, col_corr2, col_corr3 = st.columns(3)
        with col_corr1:
            corrected_tone = st.selectbox(
                "Skin Tone Selection",
                config.SUPPORTED_SKIN_TONES,
                index=config.SUPPORTED_SKIN_TONES.index(skin_res.get("skin_tone", "Fair"))
                if skin_res.get("skin_tone") in config.SUPPORTED_SKIN_TONES else 0
            )
        with col_corr2:
            corrected_under = st.selectbox(
                "Undertone Selection",
                config.SUPPORTED_UNDERTONES,
                index=config.SUPPORTED_UNDERTONES.index(skin_res.get("undertone", "Warm"))
                if skin_res.get("undertone") in config.SUPPORTED_UNDERTONES else 0
            )
        with col_corr3:
            corrected_shape = st.selectbox(
                "Body Shape Silhouette",
                config.SUPPORTED_BODY_SHAPES,
                index=config.SUPPORTED_BODY_SHAPES.index(body_res.get("body_shape", "Rectangle / Hourglass"))
                if body_res.get("body_shape") in config.SUPPORTED_BODY_SHAPES else 0
            )

        if st.button("💾 Apply Confirmed Profile", use_container_width=True):
            st.session_state["analysis_results"]["skin"]["skin_tone"] = corrected_tone
            st.session_state["analysis_results"]["skin"]["undertone"] = corrected_under
            st.session_state["analysis_results"]["body"]["body_shape"] = corrected_shape
            st.success("✅ Profile parameters confirmed for recommendation engine!")


# ==============================================================================
# PAGE 3: MY PROFILE
# ==============================================================================
elif page == "My Profile":
    st.markdown('<div class="main-title">User Profile & Physical Measurements</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Persistent storage for physical measurements, style affinities, and budget limits.</div>', unsafe_allow_html=True)

    user_id = st.session_state["user_id"]
    user_row = pm.get_or_create_user(user_id)
    latest_meas = pm.get_latest_measurements(user_id)
    saved_prefs = pm.get_preferences(user_id) or {}

    col_prof1, col_prof2 = st.columns([1, 1])

    with col_prof1:
        st.subheader("📏 Physical Measurements")
        st.caption("Distinguishes user-verified manual entries from camera estimates. Missing values are completely fine.")

        with st.form("measurements_form"):
            h_val = float(latest_meas["height_cm"]) if latest_meas and latest_meas.get("height_cm") else 170.0
            sh_val = float(latest_meas["shoulder_cm"]) if latest_meas and latest_meas.get("shoulder_cm") else 42.0
            ch_val = float(latest_meas["chest_cm"]) if latest_meas and latest_meas.get("chest_cm") else 96.0
            w_val = float(latest_meas["waist_cm"]) if latest_meas and latest_meas.get("waist_cm") else 82.0
            hip_val = float(latest_meas["hip_cm"]) if latest_meas and latest_meas.get("hip_cm") else 98.0

            m_height = st.number_input("Height (cm)", 50.0, 250.0, h_val, step=0.5)
            m_shoulder = st.number_input("Shoulder Width (cm)", 20.0, 100.0, sh_val, step=0.5)
            m_chest = st.number_input("Chest Circumference (cm)", 30.0, 200.0, ch_val, step=0.5)
            m_waist = st.number_input("Waist Circumference (cm)", 30.0, 200.0, w_val, step=0.5)
            m_hip = st.number_input("Hip Circumference (cm)", 30.0, 200.0, hip_val, step=0.5)

            save_meas_btn = st.form_submit_button("💾 Save Manual Measurements")

            if save_meas_btn:
                ok, err = pm.save_measurements(
                    user_id=user_id,
                    height_cm=m_height,
                    shoulder_cm=m_shoulder,
                    chest_cm=m_chest,
                    waist_cm=m_waist,
                    hip_cm=m_hip,
                    source="manual",
                )
                if ok:
                    st.success("✅ Manual measurements saved successfully!")
                    st.rerun()
                else:
                    st.error(f"Error saving measurements: {err}")

        if latest_meas:
            st.caption(f"Last recorded via **{latest_meas['measurement_source']}** on `{latest_meas['created_at']}`")

    with col_prof2:
        st.subheader("🎨 Clothing Style Preferences")

        with st.form("preferences_form"):
            curr_styles = saved_prefs.get("preferred_styles", "Classic")
            curr_colours = saved_prefs.get("preferred_colours", "Blue")
            curr_occasions = saved_prefs.get("preferred_occasions", "Casual")
            curr_cats = saved_prefs.get("preferred_categories", "Shirts, Formal wear")
            curr_bmin = float(saved_prefs.get("budget_min", 500.0))
            curr_bmax = float(saved_prefs.get("budget_max", 8000.0))

            p_styles = st.multiselect(
                "Preferred Styles",
                config.SUPPORTED_STYLES,
                default=[s.strip() for s in curr_styles.split(",") if s.strip() in config.SUPPORTED_STYLES] or ["Classic"]
            )
            p_colours = st.multiselect(
                "Preferred Colours",
                ["Blue", "Black", "White", "Navy", "Grey", "Red", "Emerald", "Gold", "Pastel"],
                default=[c.strip() for c in curr_colours.split(",") if c.strip() in ["Blue", "Black", "White", "Navy", "Grey", "Red", "Emerald", "Gold", "Pastel"]] or ["Blue"]
            )
            p_occasions = st.multiselect(
                "Preferred Occasions",
                config.SUPPORTED_OCCASIONS,
                default=[o.strip() for o in curr_occasions.split(",") if o.strip() in config.SUPPORTED_OCCASIONS] or ["Casual"]
            )
            p_categories = st.multiselect(
                "Preferred Clothing Categories",
                config.SUPPORTED_CATEGORIES,
                default=[cat.strip() for cat in curr_cats.split(",") if cat.strip() in config.SUPPORTED_CATEGORIES] or ["Shirts", "Formal wear"]
            )

            c_b1, c_b2 = st.columns(2)
            with c_b1:
                b_min = st.number_input("Budget Minimum (Rs.)", 0.0, 50000.0, curr_bmin, step=100.0)
            with c_b2:
                b_max = st.number_input("Budget Maximum (Rs.)", 100.0, 100000.0, curr_bmax, step=500.0)

            save_prefs_btn = st.form_submit_button("💾 Save Style Preferences")

            if save_prefs_btn:
                ok, err = pm.save_preferences(
                    user_id=user_id,
                    preferred_styles=", ".join(p_styles),
                    preferred_colours=", ".join(p_colours),
                    preferred_occasions=", ".join(p_occasions),
                    preferred_categories=", ".join(p_categories),
                    budget_min=b_min,
                    budget_max=b_max,
                )
                if ok:
                    st.success("✅ Preferences saved successfully!")
                    st.rerun()
                else:
                    st.error(f"Error saving preferences: {err}")

    st.markdown("---")
    st.subheader("🗑️ Privacy & Data Deletion")
    st.caption("You may permanently purge your profile, measurements, and all recommendation history.")
    if st.button("Delete Entire Profile & History", type="secondary"):
        if pm.delete_profile(user_id):
            st.session_state["uploaded_image_bgr"] = None
            st.session_state["analysis_results"] = None
            st.success("✅ Profile and associated records deleted.")
            st.rerun()


# ==============================================================================
# PAGE 4: OUTFIT RECOMMENDATIONS
# ==============================================================================
elif page == "Outfit Recommendations":
    st.markdown('<div class="main-title">Personalized Outfit Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Synthesizing TF-IDF keyword indexing, CLIP visual features, and Gradient Boosting classification.</div>', unsafe_allow_html=True)

    user_id = st.session_state["user_id"]
    saved_prefs = pm.get_preferences(user_id) or {}
    analysis = st.session_state.get("analysis_results")

    # Extract user features
    skin_tone = analysis["skin"]["skin_tone"] if analysis else "Medium/Wheatish"
    undertone = analysis["skin"]["undertone"] if analysis else "Warm"
    body_shape = analysis["body"]["body_shape"] if analysis else "Rectangle / Hourglass"
    user_img = st.session_state.get("uploaded_image_bgr")

    # Filters and search row
    with st.expander("🔍 Search Filters & Directives", expanded=True):
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            query_input = st.text_input("Keywords / Aesthetic", placeholder="e.g. silk wedding sherwani, summer linen")
        with col_f2:
            cat_filter = st.selectbox("Category Filter", ["All"] + config.SUPPORTED_CATEGORIES)
        with col_f3:
            occ_filter = st.selectbox("Occasion Filter", ["All"] + config.SUPPORTED_OCCASIONS)
        with col_f4:
            budget_cap = st.number_input("Max Budget (Rs.)", 500.0, 50000.0, float(saved_prefs.get("budget_max", 15000.0)), step=500.0)

    # Run recommendation
    rec_results = engine.recommend(
        user_img_bgr=user_img,
        query_text=query_input,
        preferred_styles=saved_prefs.get("preferred_styles", "Classic"),
        preferred_colours=saved_prefs.get("preferred_colours", "Blue"),
        preferred_occasions=occ_filter if occ_filter != "All" else saved_prefs.get("preferred_occasions", "Casual"),
        preferred_categories=cat_filter if cat_filter != "All" else None,
        budget_min=float(saved_prefs.get("budget_min", 0.0)),
        budget_max=budget_cap,
        skin_tone=skin_tone,
        undertone=undertone,
        body_shape=body_shape,
        weights=custom_weights,
        top_k=6,
    )

    # Status Banner
    st.markdown(
        f"""
        <div style="background-color: #1e293b; border-left: 4px solid #6366f1; padding: 12px; margin-bottom: 20px; border-radius: 4px;">
            <b>🧠 ML Predicted Category:</b> <span class="badge-pill badge-primary">{rec_results['gbm_predicted_category'] or 'All'}</span>
            &nbsp;|&nbsp; <b>Confidence:</b> {f"{rec_results['gbm_confidence'] * 100:.1f}%" if rec_results['gbm_confidence'] else 'N/A'}
            &nbsp;|&nbsp; <b>Visual Embedding (CLIP):</b> <span class="badge-pill {'badge-success' if user_img is not None else 'badge-warning'}">{'Active' if user_img is not None else 'No Photo (Text Only)'}</span>
            &nbsp;|&nbsp; <b>Eligible Items:</b> {rec_results['total_candidates']}
        </div>
        """,
        unsafe_allow_html=True,
    )

    recs = rec_results["recommendations"]

    if not recs:
        st.warning("No outfits match your exact budget or category filter combination. Try adjusting filter limits above.")
    else:
        # Display cards in a 3-column grid
        grid_cols = st.columns(3)
        for idx, item in enumerate(recs):
            col_target = grid_cols[idx % 3]
            with col_target:
                # Load image
                img_path = item["image_path"]
                abs_img_path = os.path.join(config.BASE_DIR, img_path) if not os.path.isabs(img_path) else img_path

                if os.path.exists(abs_img_path):
                    try:
                        pil_img = Image.open(abs_img_path)
                        st.image(pil_img, use_container_width=True)
                    except Exception:
                        st.image(abs_img_path, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x500?text=Outfit+Preview", use_container_width=True)

                st.markdown(f"#### {item['outfit_name']}")
                st.markdown(f"**Rs. {item['price']:.0f}** &nbsp;•&nbsp; `{item['category']}` &nbsp;•&nbsp; `{item['occasion']}`")
                st.caption(item["description"][:110] + "...")

                # Metrics
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Match Score", f"{item['final_score'] * 100:.1f}%")
                with m2:
                    st.metric("Text TF-IDF", f"{item['component_scores']['tfidf_score']:.3f}")

                st.markdown(f"**Why Recommended:**")
                st.info(item["summary_reason"])

                # Record to history action
                if st.button(f"📌 Save to History", key=f"hist_btn_{item['outfit_id']}", use_container_width=True):
                    pm.record_recommendation(
                        user_id=user_id,
                        outfit_id=item["outfit_id"],
                        outfit_name=item["outfit_name"],
                        category=item["category"],
                        match_score=item["final_score"],
                        reason=item["summary_reason"],
                    )
                    st.success(f"Saved {item['outfit_name']} to history!")


# ==============================================================================
# PAGE 5: HISTORY
# ==============================================================================
elif page == "History":
    st.markdown('<div class="main-title">Recommendation History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Chronological record of previously recommended and saved apparel items.</div>', unsafe_allow_html=True)

    user_id = st.session_state["user_id"]
    hist_items = pm.get_recommendation_history(user_id, limit=30)

    if not hist_items:
        st.info("No outfits recorded in your history yet. Explore recommendations and click 'Save to History'.")
    else:
        col_h_actions = st.columns([4, 1])
        with col_h_actions[1]:
            if st.button("🧹 Clear History", use_container_width=True):
                pm.clear_history(user_id)
                st.success("History cleared.")
                st.rerun()

        hist_df = pd.DataFrame(hist_items)
        st.dataframe(
            hist_df[["created_at", "outfit_id", "outfit_name", "category", "match_score", "recommendation_reason"]],
            use_container_width=True,
            column_config={
                "created_at": "Timestamp",
                "outfit_name": "Outfit Name",
                "category": "Category",
                "match_score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=1),
                "recommendation_reason": "Recommendation Basis",
            }
        )


# ==============================================================================
# PAGE 6: MODEL EVALUATION
# ==============================================================================
elif page == "Model Evaluation":
    st.markdown('<div class="main-title">Machine Learning Model Diagnostics & Evaluation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Held-out test set metrics, confusion matrix, and training provenance for Gradient Boosting.</div>', unsafe_allow_html=True)

    metrics = report_evaluation_metrics()

    st.markdown("""
    > [!NOTE]
    > **Offline Evaluation vs. Real-Time Recommendations:**
    > The evaluation metrics below measure the **Gradient Boosting Classifier's** capacity to predict clothing category preferences from profile attributes on an independent held-out test split. In live recommendations, this classifier operates as one component alongside TF-IDF semantic search and CLIP image embeddings.
    """)

    if metrics is None:
        st.warning("No saved model metrics found. Click below to train the Gradient Boosting model.")
        if st.button("🚀 Train Model Now"):
            with st.spinner("Training GradientBoostingClassifier..."):
                metrics = train_model()
            st.success("Model trained successfully!")
            st.rerun()
    else:
        # Metric cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Accuracy", f"{metrics['accuracy'] * 100:.1f}%")
        with m_col2:
            st.metric("F1 Score (Weighted)", f"{metrics['f1_weighted']:.3f}")
        with m_col3:
            st.metric("Precision (Weighted)", f"{metrics['precision_weighted']:.3f}")
        with m_col4:
            st.metric("Recall (Weighted)", f"{metrics['recall_weighted']:.3f}")

        st.caption(
            f"Evaluated on **{metrics['test_samples']} test samples** (80% Train: {metrics['train_samples']} samples / 20% Held-Out Test). "
            f"Dataset Source: `{metrics.get('dataset_path', 'user_preference_training_data.csv')}`"
        )

        # Confusion Matrix
        st.subheader("📊 Confusion Matrix (Held-out Test Split)")
        cm_data = np.array(metrics["confusion_matrix"])
        classes = metrics["classes"]

        cm_df = pd.DataFrame(cm_data, index=classes, columns=classes)
        st.dataframe(cm_df, use_container_width=True)

        # Per-class Classification Report
        st.subheader("📋 Classification Report Breakdown")
        rep = metrics.get("classification_report", {})
        class_rows = []
        for cls_name in classes:
            if cls_name in rep:
                class_rows.append({
                    "Category": cls_name,
                    "Precision": round(rep[cls_name]["precision"], 3),
                    "Recall": round(rep[cls_name]["recall"], 3),
                    "F1-Score": round(rep[cls_name]["f1-score"], 3),
                    "Support": int(rep[cls_name]["support"]),
                })
        if class_rows:
            st.dataframe(pd.DataFrame(class_rows), use_container_width=True)

        st.markdown("---")
        st.subheader("🔄 Model Maintenance")
        if st.button("Retrain Gradient Boosting Pipeline", type="secondary"):
            with st.spinner("Refitting pipeline strictly on train split..."):
                train_model()
            st.success("✅ Model retrained and metrics updated!")
            st.rerun()
