import streamlit as st
import pandas as pd
import time
import pickle
from streamlit_extras.let_it_rain import rain  

# ---- PAGE CONFIG ----
st.set_page_config(page_title="🎓 Student Promotion Predictor", page_icon="📚", layout="wide")

# ---- LOAD MODEL ----
with open("promotion.pkl", "rb") as model_file:
    pipeline = pickle.load(model_file)

# ---- CUSTOM CSS FOR WHITE THEME ----
st.markdown("""
    <style>
        /* Background and general styling */
        .main {
            background-color: #ffffff;  /* White background */
            color: #000000;  /* Black text */
        }
        
        /* Header */
        h1, h2, h3, p {
            text-align: center;
            color: #000000;  /* Black header text */
        }
        
        /* Form Styling */
        .stNumberInput, .stSelectbox, .stTextInput, .stSlider {
            background-color: #ffffff;  /* White background */
            color: #000000;  /* Black text */
            border-radius: 8px;
            padding: 10px;
            transition: 0.3s;
        }
        
        /* Button Styling */
        div.stButton > button {
            background-color: #4CAF50;  /* Green button */
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 12px 30px;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #388E3C;  /* Darker green on hover */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }

        /* Cards */
        .card {
            background: #f9f9f9;  /* Light gray background */
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            transition: 0.3s;
            margin: 15px;
            text-align: center;
        }
        .card:hover {
            transform: scale(1.05);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
        }
        
        /* Results */
        .success {
            color: #4CAF50;  /* Green success text */
        }
        .error {
            color: #E53935;  /* Red error text */
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #000000;  /* Black footer text */
        }
    </style>
""", unsafe_allow_html=True)

# ---- HEADER ----
st.markdown("<h1>🎓 Student Promotion Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p>📊 Fill in the details to predict student promotion status.</p>", unsafe_allow_html=True)

# ---- FORM ----
with st.form("student_form"):
    # Creating a 3-column grid layout
    col1, col2, col3 = st.columns(3)

    #  Column 1
    with col1:
        age = st.number_input("📅 Age", min_value=4, max_value=18, value=10)
        parental_education = st.selectbox("🎓 Parental Education", ['High School', 'College', 'Postgraduate'])
        earning_class = st.selectbox("💰 Earning Class", ['Low', 'Medium', 'High'])

    #  Column 2
    with col2:
        level = st.selectbox("🏫 School Level", ['Kindergarten', 'Elementary', 'Middle School', 'High School'])
        course_level = st.selectbox("📘 Course Level", ['Low', 'Medium', 'High'])
        material_level = st.selectbox("📖 Material Level", ['Low', 'Medium', 'High'])

    # Column 3
    with col3:
        previous_scores = st.number_input("📊 Previous Scores (out of 100)", min_value=0, max_value=100, value=75)
        assessment_score = st.number_input("📝 Assessment Score (out of 100)", min_value=0, max_value=100, value=80)
        iq = st.number_input("🧠 IQ", min_value=50.0, max_value=140.0, value=110.0)

    # ---- Study time and Attendance ----
    study_time = st.slider("⏳ Study Time (hours/day)", min_value=0.0, max_value=20.0, value=6.0, step=0.1)
    attendance = st.slider("📅 Attendance (%)", min_value=0, max_value=100, value=85)

    submitted = st.form_submit_button("🔍 Predict")

# ---- PREDICTION ----
if submitted:
    # Preparing input data
    input_data = pd.DataFrame([[  
        age, parental_education, earning_class, level,  
        course_level, material_level, previous_scores, assessment_score,  
        iq, attendance, study_time  
    ]], columns=[  
        "Age", "Parental_Education_Level", "Earning Class", "Level",  
        "Course Level", "Material Level", "Previous_Scores", "Assesment Score",  
        "IQ", "Attendance", "Study Time"  
    ])

    # Smooth loading animation
    with st.spinner("🔄 Running prediction..."):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            progress_bar.progress(percent_complete + 1)

    # Making the prediction
    prediction = pipeline.predict(input_data)

    # ---- RESULT DISPLAY ----
    st.markdown("<h2>📊 Prediction Result</h2>", unsafe_allow_html=True)

    # Success display
    if prediction[0] == 1:
        st.success("🎉 **Promoted!** The student will be promoted! 🏆")

        # 🎉 Celebration effects
        st.balloons()  
        rain(emoji="🎉", font_size=20, falling_speed=3, animation_length="infinite")

        # Displaying result in an elegant card
        st.markdown(
            """
            <div class="card">
                <h3 class="success">✅ Promoted!</h3>
                <p>🎯 Keep up the good work! Consistent performance and dedication lead to success.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Failure display
    else:
        st.error("⚠️ **Not Promoted.** More effort needed! 📚")

        # 💡 Motivational rain effect
        rain(emoji="💡", font_size=20, falling_speed=2, animation_length="infinite")

        # Displaying result in a card
        st.markdown(
            """
            <div class="card">
                <h3 class="error">❌ Not Promoted</h3>
                <p>📚 Consider improving study time, attendance, and assessment performance.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
