import streamlit as st
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="Fruit & Vegetable Classifier",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern UI ---
st.markdown("""
    <style>
    /* --- General Styles --- */
    body {
        background-color: #f0f2f6;
    }
    .stApp {
        background-color: #f0f2f6;
    }

    /* --- Title --- */
    .main-title {
        font-size: 2.8em;
        font-weight: 700;
        color: #0d3b1e;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* --- Subheader for Cards --- */
    .card-subheader {
        font-size: 1.5em;
        font-weight: 600;
        color: #0d3b1e;
        margin-bottom: 15px;
    }

    /* --- Card UI --- */
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
        margin-top: 20px;
    }
    .card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        transform: translateY(-5px);
    }
    .card ul, .card ol {
        padding-left: 20px;
    }

    /* --- Button --- */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 12px 0;
        font-size: 1.1em;
        font-weight: 600;
        color: white;
        background-color: #2e8b57;
        border: none;
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #276a45;
        box-shadow: 0 4px 8px rgba(46, 139, 87, 0.4);
    }
    
    /* --- File Uploader Customization --- */
    [data-testid="stFileUploader"] {
        padding: 1rem;
        border-radius: 12px;
        background-color: #f8f9fa;
    }
    [data-testid="stFileUploader"] section {
        padding: 2rem;
        border: 2px dashed #2e8b57;
        background-color: #f8f9fa;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    [data-testid="stFileUploader"] section:hover {
        background-color: #e8f5e9;
    }
    [data-testid="stFileUploader"] .st-emotion-cache-1gulkj5 { 
        font-size: 1.2em;
        font-weight: 500;
        text-align: center;
    }
    [data-testid="stFileUploader"] button { 
        background-color: #ffffff;
        color: #2e8b57;
        border: 1px solid #2e8b57;
        font-weight: bold;
    }
    [data-testid="stFileUploader"] button:hover {
        background-color: #2e8b57;
        color: #ffffff;
    }

    /* --- Result Display --- */
    .result-container {
        margin-top: 30px;
        padding: 20px;
        background-color: #e8f5e9;
        border-radius: 12px;
        border-left: 8px solid #2e8b57;
    }
    .result-text {
        font-size: 1.6em;
        font-weight: 700;
        color: #0d3b1e;
        text-align: center;
    }
    .confidence-text {
        font-size: 1.1em;
        color: #555;
        text-align: center;
    }

    </style>
""", unsafe_allow_html=True)


# --- Model and Class Labels ---
CLASS_LABELS = [
    'Apple Healthy', 'Apple Rotten', 'Banana Healthy', 'Banana Rotten',
    'Carrot Healthy', 'Carrot Rotten', 'Potato Healthy', 'Potato Rotten'
]

@st.cache_resource
def load_saved_model():
    """Loads the pre-trained Keras model from disk."""
    try:
        model = load_model('fruit_vegetable_disease_model.keras')
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_saved_model()


# --- Main Application ---
st.markdown('<div class="main-title">Fruit & Vegetable Classifier</div>', unsafe_allow_html=True)
st.image("Classification.jpg")
st.info("Upload an image to classify its condition (Healthy or Rotten).")

# --- Main interactive card (REFACTORED) ---
# We wrap the entire interactive section in a single card div.
# The st.container from the previous version was removed to simplify the render tree.
# st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

if uploaded_file is not None and model is not None:
    col1, col2 = st.columns([2, 1])

    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        st.write("### Actions")
        predict_button = st.button("Classify Condition")

    if predict_button:
        with st.spinner('Analyzing the image...'):
            file_bytes = np.array(image.convert('RGB'))
            img = cv2.resize(file_bytes, (128, 128))
            img_input = img.astype('float32') / 255.0
            img_input = np.expand_dims(img_input, axis=0)

            prediction = model.predict(img_input)
            score = np.max(prediction)
            predicted_class_index = np.argmax(prediction)
            predicted_class = CLASS_LABELS[predicted_class_index]

            st.markdown(
                f"""
                <div class="result-container">
                    <p class="result-text">Prediction: {predicted_class}</p>
                    <p class="confidence-text">Confidence: {score:.2%}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown('</div>', unsafe_allow_html=True) # Closes the main card div

# --- Static Content Sections ---
about_project_content = """
<div class="card">
    <p class="card-subheader">ℹ️ About This Project</p>
    <p>This application leverages a deep learning model to classify the condition of fruits and vegetables from an uploaded image. The primary goal is to provide a quick and accessible tool for farmers, vendors, and consumers to assess the quality of produce.</p>
    <strong>How to Use:</strong>
    <ol>
        <li>Drag and drop an image or click the 'Browse files' button to upload a picture of a fruit or vegetable.</li>
        <li>Click the <strong>'Classify Condition'</strong> button.</li>
        <li>The model will analyze the image and predict whether the item is 'Healthy' or 'Rotten', displaying the result along with a confidence score.</li>
    </ol>
    <p>This tool is a demonstration of the practical applications of computer vision in agriculture and quality control.</p>
</div>
"""
st.markdown(about_project_content, unsafe_allow_html=True)

model_details_content = """
<div class="card">
    <p class="card-subheader">⚙️ Model Details</p>
    <p>The classification is performed by a <strong>Convolutional Neural Network (CNN)</strong>, a deep learning architecture specifically designed for image analysis tasks.</p>
    <ul>
        <li><strong>Model Type:</strong> Convolutional Neural Network (CNN)</li>
        <li><strong>Framework:</strong> TensorFlow / Keras</li>
        <li><strong>Input Shape:</strong> The model expects an input image resized to `128x128` pixels with 3 color channels (RGB).</li>
        <li><strong>Output Classes:</strong> The model can classify 8 categories for Apples, Bananas, Carrots, and Potatoes (Healthy/Rotten).</li>
        <li><strong>Training:</strong> The model was trained on a labeled dataset of thousands of images, enabling it to learn the distinct visual features (like color, spots, texture, and mold) that differentiate between healthy and rotten produce.</li>
    </ul>
</div>
"""
st.markdown(model_details_content, unsafe_allow_html=True)

if model is None:
    st.error("Model could not be loaded. Please ensure 'fruit_vegetable_disease_model.keras' is in the correct directory.")