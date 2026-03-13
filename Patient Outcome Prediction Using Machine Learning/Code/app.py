import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go


# -------------------
# Custom CSS Styling
# -------------------
CUSTOM_CSS = """
<style>
body, .stApp {
    font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
    background: var(--background-color);
    color: #222831 !important; /* Improved font color for both light and dark */
}

[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: #fff;
}

.stButton>button, .stTextInput>div>input, .stSelectbox>div>div>div>input, .stSlider>div {
    border-radius: 10px !important;
    box-shadow: 0 2px 8px rgba(30,41,59,0.08);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    background: #f1f5f9;
    color: #222831;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: #fff !important;
}

.stMarkdown, .stDataFrame, .stTable {
    border-radius: 12px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(30,41,59,0.06);
    padding: 1rem;
    color: #222831 !important;
}

.stAlert {
    border-radius: 10px;
}

.stTextArea>div>textarea {
    border-radius: 10px !important;
    color: #222831 !important;
}

.st-bb {
    font-size: 1.1rem;
    font-weight: 500;
    color: #222831 !important;
}
</style>
"""

# -------------------
# Load Model Pipeline
# -------------------
@st.cache_resource(show_spinner=True)
def load_model():
    with open("output/model_pipeline.pkl", "rb") as f:
        model = pickle.load(f)
    return model

model = load_model()

# -------------------
# Helper Functions
# -------------------
def get_feature_info():
    # These should match your model's expected features
    # You may need to adjust based on your actual data
    return {
        'age': {'type': 'slider', 'min': 0, 'max': 100, 'step': 1, 'help': 'Patient age in years.'},
        'num_procedures': {'type': 'slider', 'min': 0, 'max': 10, 'step': 1, 'help': 'Number of procedures during stay.'},
        'days_in_hospital': {'type': 'slider', 'min': 1, 'max': 30, 'step': 1, 'help': 'Length of stay (days).'},
        'comorbidity_score': {'type': 'slider', 'min': 0, 'max': 10, 'step': 1, 'help': 'Comorbidity index score.'},
        'gender': {'type': 'select', 'options': ['Male', 'Female', 'Other'], 'help': 'Patient gender.'},
        'primary_diagnosis': {'type': 'select', 'options': ['Diabetes', 'Heart Failure', 'COPD', 'Other'], 'help': 'Main diagnosis.'},
        'discharge_to': {'type': 'select', 'options': ['Home', 'Rehab', 'Nursing Facility', 'Other'], 'help': 'Discharge destination.'},
    }

# For SHAP-style explanation (dummy, as true SHAP requires more setup)
def get_top_features(input_df, model, n=3):
    # Use feature importances from RandomForest if available
    try:
        importances = model.named_steps['classifier'].feature_importances_
        # Get feature names after preprocessing
        ohe = model.named_steps['preprocessor'].named_transformers_['cat'].named_steps['onehot']
        cat_cols = model.named_steps['preprocessor'].transformers_[1][2]
        num_cols = model.named_steps['preprocessor'].transformers_[0][2]
        ohe_features = ohe.get_feature_names_out(cat_cols)
        all_features = np.concatenate([num_cols, ohe_features])
        top_idx = np.argsort(importances)[::-1][:n]
        return [(all_features[i], importances[i]) for i in top_idx]
    except Exception:
        return []

# -------------------
# Sidebar
# -------------------
st.set_page_config(page_title="Hospital Readmission Predictor", layout="wide", initial_sidebar_state="expanded")
# st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.title("🏥 Readmission Predictor")
    st.markdown("""
    <span style='font-size:1.1em;'>Predict the risk of hospital readmission for patients using a machine learning model.</span>
    """, unsafe_allow_html=True)
    st.divider()
    # st.write('---')
    nav = st.radio("Navigation", ["Predict", "Dataset Summary", "About Model", "FAQ"], key="nav")
    st.divider()
    # st.markdown("**Theme:**")
    # dark_mode = st.toggle("Dark Mode", value=False)
    # st.divider()
    st.markdown("**Feedback**")
    feedback = st.text_area("Suggestions or feedback?", placeholder="Type here...")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")

# -------------------
# Main Content
# -------------------
if nav == "Predict":
    st.header("Patient Readmission Risk Prediction")
    st.markdown("Enter patient details below to predict the risk of readmission.")
    feature_info = get_feature_info()
    input_data = {}
    cols = st.columns(2)
    for i, (feat, info) in enumerate(feature_info.items()):
        with cols[i % 2]:
            if info['type'] == 'slider':
                input_data[feat] = st.slider(feat.replace('_', ' ').title(), min_value=info['min'], max_value=info['max'], step=info['step'], help=info['help'])
            elif info['type'] == 'select':
                input_data[feat] = st.selectbox(feat.replace('_', ' ').title(), options=info['options'], help=info['help'])
    input_df = pd.DataFrame([input_data])
    st.divider()
    predict_btn = st.button("Predict Readmission Risk", type="primary")
    if predict_btn:
        with st.spinner("Predicting..."):
            try:
                proba = model.predict_proba(input_df)[0]
                pred = model.predict(input_df)[0]
                risk_label = "High Risk" if pred == 1 else "Low Risk"
                risk_color = "#ef4444" if pred == 1 else "#22c55e"
                st.markdown(f"### Prediction: <span style='color:{risk_color}'>{risk_label}</span>", unsafe_allow_html=True)
                # Probability gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = proba[1],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Readmission Probability", 'font': {'size': 20}},
                    gauge = {
                        'axis': {'range': [0, 1]},
                        'bar': {'color': risk_color},
                        'steps' : [
                            {'range': [0, 0.5], 'color': '#d1fae5'},
                            {'range': [0.5, 1], 'color': '#fee2e2'}
                        ],
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"**Model Confidence:** {proba[1]*100:.1f}% for High Risk")
                # SHAP-style explanation
                top_feats = get_top_features(input_df, model)
                if top_feats:
                    st.markdown("#### Top Contributing Features:")
                    for f, imp in top_feats:
                        st.markdown(f"- **{f}**: {imp:.3f}")
                else:
                    st.info("Feature importance explanation not available.")
            except Exception as e:
                st.error(f"Prediction failed: {e}")

elif nav == "Dataset Summary":
    st.header("Dataset Summary")
    # Try to load train_df.csv
    try:
        df = pd.read_csv("train_df.csv")
        st.markdown(f"**Rows:** {df.shape[0]}  ")
        st.markdown(f"**Columns:** {df.shape[1]}")
        st.dataframe(df.head(20))
        st.markdown("#### Column Info:")
        st.dataframe(df.describe(include='all').T)
    except Exception as e:
        st.error(f"Could not load dataset: {e}")

elif nav == "About Model":
    st.header("About the Model")
    st.markdown("""
    - **Model:** Random Forest Classifier (with preprocessing pipeline)
    - **Features:** Age, Number of Procedures, Days in Hospital, Comorbidity Score, Gender, Primary Diagnosis, Discharge To
    - **Target:** Readmitted (binary)
    - **Training Data:** See 'Dataset Summary' tab
    - **Performance:** See notebook for metrics
    - **Deployment:** This app loads the trained model and predicts in real time.
    """)
    st.info("For more details, see the project notebook.")

elif nav == "FAQ":
    st.header("Frequently Asked Questions")
    st.markdown("""
    **Q: What is this app for?**  
    A: It predicts the risk of hospital readmission for a patient based on input features.

    **Q: How accurate is the model?**  
    A: See the notebook for detailed metrics. The model is trained and validated on historical data.

    **Q: Is my data saved?**  
    A: No, all predictions are local and not stored.

    **Q: Who can use this?**  
    A: Healthcare professionals, researchers, or anyone interested in patient outcome prediction.
    """)
    st.success("Still have questions? Use the feedback form in the sidebar!")


