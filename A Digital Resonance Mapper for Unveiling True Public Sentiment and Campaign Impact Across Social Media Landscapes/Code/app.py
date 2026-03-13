import streamlit as st
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import joblib
import os
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# --- NLTK Downloads ---
# This function ensures that the necessary NLTK data is downloaded once and cached.
@st.cache_resource
def download_nltk_data():
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('vader_lexicon')
download_nltk_data()

# --- Data Loading and Preprocessing ---
@st.cache_data
def load_data():
    # This function loads the dataset from the CSV file for the visualization page.
    # It's cached to avoid reloading the data on every interaction.
    data = pd.read_csv("Mental-Health-Twitter.csv")
    df = data[['post_text', 'label']]
    df.dropna(subset=['post_text', 'label'], inplace=True)
    return df

def preprocess_text(text):
    # This function cleans and preprocesses a single piece of text for prediction.
    # It performs lowercasing, removes special characters, tokenizes, removes stopwords, and applies stemming/lemmatization.
    text = text.lower()
    text = re.sub(r"http\S+|@\S+|[^A-Za-z\s]", '', text)
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    words = word_tokenize(text)
    words = [word for word in words if word not in stopwords.words('english')]
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

# --- Model Loading ---
@st.cache_resource
def load_model_and_vectorizer():
    """
    Loads the pre-trained logistic regression model and the TF-IDF vectorizer from disk.
    The function is cached to ensure the models are loaded only once per session.
    """
    model_path = 'mental_health_model.pkl'
    tfidf_path = 'tfidf_vectorizer.pkl'

    if os.path.exists(model_path) and os.path.exists(tfidf_path):
        model = joblib.load(model_path)
        tfidf = joblib.load(tfidf_path)
        return model, tfidf
    else:
        # If model files are not found, display an error and stop the app execution.
        st.error("Model files not found. Please run the `train_model.py` script first to generate them.")
        st.stop()
        
# --- Load initial data and model ---
df = load_data()
model, tfidf = load_model_and_vectorizer()
sia = SentimentIntensityAnalyzer()

# --- Streamlit App UI ---
st.set_page_config(layout="wide", page_title="Mental Health Analysis")

# Custom CSS for a modern and clean user interface.
st.markdown("""
<style>
    .reportview-container {
        background: #e9e7fd;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    h1, h2, h3 {
        color: #333;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
    }
    .stTextArea textarea {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 1.1em;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .result-card {
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,0.1);
    }
    .result-card-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .result-card-text {
        font-size: 1.2em;
        color: #555;
    }
    .positive-text { color: #28a745; }
    .negative-text { color: #dc3545; }
    .neutral-text { color: #6c757d; }
    .icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    .home-image {
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Page Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Analysis", "Visualizations"])

if page == "Home":
    st.title("Welcome to the Senti-Mental Health Analysis App")
    
    st.markdown('<div class="home-image">', unsafe_allow_html=True)
    try:
        image = Image.open('sentiment-analysis.jpg')
        st.image(image, caption='Sentiment Analysis', use_container_width=True)
    except FileNotFoundError:
        st.error("Home page image not found. Please make sure '3-tips-sentiment-analysis.webp' is in the same directory.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.header("About the App")
    st.markdown("""
    This application leverages Natural Language Processing (NLP) to provide insights into textual data. It offers two main functionalities:
    
    - **Mental Health Concern Prediction:** Using a Logistic Regression model trained on a dataset of Twitter posts, this tool predicts whether a given text may indicate a potential mental health concern.
    - **Sentiment Analysis:** Powered by the VADER sentiment analysis tool, it determines the emotional tone of the text, classifying it as positive, negative, or neutral.
    
    Navigate to the **Analysis** page to try it out with your own text, or visit the **Visualizations** page to explore the data that powers our model.
    """, unsafe_allow_html=True)


elif page == "Analysis":
    st.title("Text-Based Senti-Mental Health Analysis")
    st.markdown("This application analyzes the text you enter to predict potential mental health concerns and determine its sentiment.")
    
    user_input = st.text_area("Enter text for analysis:", "", height=150)

    if st.button("Analyze"):
        if user_input:
            # Preprocess, vectorize, and predict on user input
            cleaned_input = preprocess_text(user_input)
            input_vector = tfidf.transform([cleaned_input]).toarray()
            prediction = model.predict(input_vector)
            
            # Perform sentiment analysis
            sentiment_score = sia.polarity_scores(user_input)
            compound_score = sentiment_score['compound']
            if compound_score >= 0.05:
                sentiment = "Positive"
                sentiment_color = "positive-text"
                sentiment_icon = "😊"
            elif compound_score <= -0.05:
                sentiment = "Negative"
                sentiment_color = "negative-text"
                sentiment_icon = "😞"
            else:
                sentiment = "Neutral"
                sentiment_color = "neutral-text"
                sentiment_icon = "😐"

            # Display results in styled columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                if prediction[0] == 1:
                    st.markdown('<div class="icon">⚠️</div>', unsafe_allow_html=True)
                    st.markdown('<p class="result-card-title">Prediction</p>', unsafe_allow_html=True)
                    st.markdown('<p class="result-card-text negative-text">Potential mental health concern detected.</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="icon">✅</div>', unsafe_allow_html=True)
                    st.markdown('<p class="result-card-title">Prediction</p>', unsafe_allow_html=True)
                    st.markdown('<p class="result-card-text positive-text">No potential mental health concern detected.</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="icon">{sentiment_icon}</div>', unsafe_allow_html=True)
                st.markdown('<p class="result-card-title">Sentiment</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="result-card-text {sentiment_color}">{sentiment}</p>', unsafe_allow_html=True)
                st.progress( (compound_score + 1) / 2 ) # Normalize score to 0-1 for progress bar
                st.markdown(f'<p class="result-card-text" style="font-size: 1em;">Compound Score: {compound_score:.2f}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter some text to analyze.")

elif page == "Visualizations":
    st.title("Data Visualizations")
    st.markdown("These visualizations are based on the dataset used to train the model.")

    df_vis = df.copy()
    df_vis['cleaned_text'] = df_vis['post_text'].apply(preprocess_text)

    # --- Most Common Words Plot (Plotly) ---
    st.subheader("Top 20 Most Common Words")
    all_words = [word for text in df_vis['cleaned_text'] for word in word_tokenize(text)]
    word_freq = Counter(all_words)
    common_words_df = pd.DataFrame(word_freq.most_common(20), columns=['Word', 'Frequency'])
    fig1 = px.bar(common_words_df, x='Word', y='Frequency', title="Top 20 Most Common Words in Tweets",
                  color='Frequency', color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig1, use_container_width=True)

    # --- Tweet Length Distribution (Plotly) ---
    st.subheader("Tweet Length Distribution")
    df_vis['tweet_length'] = df_vis['cleaned_text'].apply(lambda x: len(x.split()))
    fig2 = px.histogram(df_vis, x='tweet_length', nbins=30, title="Tweet Length Distribution",
                        color_discrete_sequence=['purple'])
    st.plotly_chart(fig2, use_container_width=True)

    # --- Word Cloud ---
    st.subheader("Word Cloud of Common Terms")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(df_vis['cleaned_text']))
    fig3, ax3 = plt.subplots()
    ax3.imshow(wordcloud, interpolation='bilinear')
    ax3.axis("off")
    st.pyplot(fig3)

    # --- Sentiment Distribution (Plotly) ---
    st.subheader("Sentiment Distribution in Dataset")
    df_vis['sentiment_score'] = df_vis['post_text'].apply(lambda text: sia.polarity_scores(text)['compound'])
    df_vis['sentiment'] = df_vis['sentiment_score'].apply(lambda score: "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral")
    sentiment_counts = df_vis['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    fig4 = px.bar(sentiment_counts, x='Sentiment', y='Count', title="Sentiment Distribution in Dataset",
                  color='Sentiment', color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'})
    st.plotly_chart(fig4, use_container_width=True)
