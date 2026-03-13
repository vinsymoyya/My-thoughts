# Hospital Readmission Prediction Web App

A modern, interactive Streamlit web application for predicting hospital readmission risk using a trained machine learning model. This app is designed for healthcare professionals, researchers, and anyone interested in patient outcome prediction.

---

## Features

- **Patient Data Input:**
  - Intuitive widgets for entering patient details (sliders, dropdowns, etc.)
  - Responsive, two-column layout for easy data entry
- **Prediction Display:**
  - Real-time prediction of readmission risk ("High Risk" or "Low Risk")
  - Probability gauge chart and model confidence display
  - SHAP-style feature importance (top contributing features)
- **Sidebar Navigation:**
  - Tabs: Predict, Dataset Summary, About Model, FAQ
  - Information tooltips and About section
  - Feedback form for user suggestions
  - (Optional) Dark/Light mode toggle
- **Dataset Summary:**
  - View sample data, column info, and statistics
- **Styling:**
  - Custom CSS for a modern, professional look
  - Rounded boxes, shadows, and custom fonts
  - Color scheme optimized for both light and dark modes
- **Deployment Ready:**
  - Launch with `streamlit run app.py`
  - Error handling, loading spinners, and caching for speed

---

## File Structure

```
├── app.py                      # Main Streamlit app
├── train_df.csv                # Training dataset
├── test_df.csv                 # Test dataset
├── output/
│   ├── model_pipeline.pkl      # Trained model pipeline (RandomForest + preprocessing)
│   ├── classification_report.json
│   ├── confusion_matrix.csv
│   ├── confusion_matrix_heatmap.png
├── hospital-readmission-prediction-v1.ipynb  # Development notebook
├── README.md                   # This file
```

---

## How to Run

1. **Install Requirements**
   - Python 3.8+
   - Install dependencies:
     ```bash
     pip install streamlit pandas numpy scikit-learn plotly
     ```

2. **Ensure Model File Exists**
   - The app expects `output/model_pipeline.pkl` (created from the notebook).

3. **Launch the App**
   ```bash
   streamlit run app.py
   ```
   - The app will open in your browser.

---

## Usage

- Go to the **Predict** tab, enter patient details, and click **Predict Readmission Risk**.
- View the risk label, probability gauge, and top contributing features.
- Explore the **Dataset Summary** and **About Model** tabs for more information.
- Use the **FAQ** tab for common questions.
- Submit feedback via the sidebar form.

---

## Model Details

- **Type:** Random Forest Classifier (with preprocessing pipeline)
- **Features:** Age, Number of Procedures, Days in Hospital, Comorbidity Score, Gender, Primary Diagnosis, Discharge To
- **Target:** Readmitted (binary)
- **Training Data:** See `train_df.csv`
- **Performance:** See `output/classification_report.json` and the notebook

---

## Customization

- To change feature options or ranges, edit the `get_feature_info()` function in `app.py`.
- To update the model, retrain in the notebook and overwrite `output/model_pipeline.pkl`.
- For advanced explanations, integrate SHAP or LIME (see comments in `app.py`).

---
