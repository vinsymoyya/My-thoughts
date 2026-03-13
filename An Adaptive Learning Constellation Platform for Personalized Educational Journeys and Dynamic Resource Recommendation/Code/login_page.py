import streamlit as st
import re

# Page Configuration - Full Screen Mode
st.set_page_config(page_title="Student Login", page_icon="🎓", layout="wide")

# Corrected and Enhanced Custom CSS
st.markdown(
    """
    <style>
        /* Hide top-left decoration */
        [data-testid="stDecoration"] { display: none; }

        /* Main container for centering content */
        .block-container {
            padding: 2rem 1rem 1rem 1rem !important;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        /* Page background */
        .stApp {
            background: linear-gradient(135deg, #F0F2F6, #FFFFFF);
            color: #333333;
        }

        /* Title styling */
        .login-title, .dashboard-title {
            text-align: center;
            color: #0068C9;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 2rem;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Login Form Container */
        [data-testid="stForm"] {
            background: #FFFFFF;
            padding: 2.5rem;
            border-radius: 10px;
            box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.1);
            width: 100%;
            border: 1px solid #E0E0E0;
        }

        /* Default Button Style */
        .stButton>button {
            background-color: #0068C9;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
            border: none;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #0055A4;
            transform: scale(1.02);
        }

        /* Style for smaller buttons (Login and Logout) */
        [data-testid="stForm"] .stButton>button, .logout-button .stButton>button {
            font-size: 18px;
            padding: 12px 0;
        }

        /* **NEW**: Larger style for the main dashboard tiles */
        .dashboard-container .stButton>button {
            font-size: 20px;       /* Increased font size */
            padding: 25px 10px;     /* Increased padding for more height */
            margin-bottom: 1rem;   /* Adds space between buttons in the same column */
        }

    </style>
    """,
    unsafe_allow_html=True
)

# **Session State for Page Navigation**
if "page" not in st.session_state:
    st.session_state.page = "login"

# **Login Page**
if st.session_state.page == "login":
    st.markdown('<div style="height: 20vh;"></div>', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🎓 Student Login</h1>', unsafe_allow_html=True)

    _, form_col, _ = st.columns([1,1.5,1])
    with form_col:
        with st.form(key="login_form", clear_on_submit=False):
            name = st.text_input("🧑 Name", placeholder="Enter your full name")
            age = st.number_input("📅 Age", min_value=3, max_value=24, step=1)
            level = st.selectbox("🏫 Level", ["Kindergarten", "Elementary", "Middle School", "High School"])
            email = st.text_input("📧 Email ID", placeholder="Enter your email")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔓 Login")

            if submitted:
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not name or not email:
                    st.warning("⚠️ Please enter your name and email to continue!")
                elif not re.match(email_regex, email):
                    st.error("🚫 Please enter a valid email address.")
                else:
                    st.session_state.page = "dashboard"
                    st.session_state.user = {"name": name, "age": age, "level": level, "email": email}
                    st.rerun()

# **Dashboard Page**
elif st.session_state.page == "dashboard":
    user_name = st.session_state.user.get("name", "Student")
    st.markdown(f'<h1 class="dashboard-title">📊 Welcome, {user_name}!</h1>', unsafe_allow_html=True)

    # Wrap dashboard tiles in a div with a specific class for targeted styling
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 Predict Assessment Score", use_container_width=True):
            st.switch_page("pages/PredictAssesmentScore.py")
        if st.button("📚 Recommendation", use_container_width=True):
            st.switch_page("pages/Recommendation.py")
    with col2:
        if st.button("🎓 Check Promotion", use_container_width=True):
            st.switch_page("pages/Promotion.py")
        if st.button("🔍 Resource Analysis", use_container_width=True):
            st.switch_page("pages/retentionSkip.py")
    st.markdown('</div>', unsafe_allow_html=True)

    # Wrap logout button in a div for separate styling
    st.markdown('<div class="logout-button">', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    _, logout_col, _ = st.columns([2.2,1,2.2])
    with logout_col:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)