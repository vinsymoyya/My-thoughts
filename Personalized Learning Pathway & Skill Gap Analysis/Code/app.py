import streamlit as st
import time
from utils import get_resume_text, get_llm, extract_text_from_url
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import base64
import os


# --- Page Configuration ---
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🤖",
    layout="wide", # Changed to wide for better tab layout
    initial_sidebar_state="collapsed"
)

# --- State Initialization ---
def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "resume_uploaded" not in st.session_state:
        st.session_state["resume_uploaded"] = False
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = ""

initialize_session_state()

# --- Background Image Function ---
@st.cache_data
def get_image_as_base64(file_path):
    """Reads a local image file and returns it as a Base64 encoded string."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# --- Background Image Function (accepts Base64 string) ---
def add_login_bg(image_base64: str):
    """Adds a background image to the page using custom CSS from a Base64 string."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{image_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# --- Login Page ---
def login_page():
    """Renders the login page and handles authentication logic."""
    # Use the Base64 function for the local image background
    img_base64 = get_image_as_base64("background image.png")
    if img_base64:
        add_login_bg(img_base64)
    else:
        # Fallback color if image is not found
        st.markdown("<style>.stApp { background-color: #e6f3ff; }</style>", unsafe_allow_html=True)

    # --- NEW: CSS to change font colors on the login page ---
    st.markdown("""
        <style>
        h1 { /* Targets the main title */
            color: white;
        }
        label { /* Targets the labels for input fields */
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # --- End of new code ---

    st.title("AI Career Assistant Login")
    USER_DATABASE = {"user": "pass", "demo": "streamlit","ganesh":"12345"}

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter Username").lower()
        password = st.text_input("Password", type="password", placeholder="Password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username in USER_DATABASE and USER_DATABASE[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Logged in successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password.")

# --- TOOL: Cold Email Generator Functions ---
def email_generator_tool():
    st.subheader("📮 Craft a Professional Cold Email")
    parser = JsonOutputParser()
    llm = get_llm()
    resume_text = st.session_state.get("resume_text")
    
    def get_job_details_from_text(text: str):
        prompt = PromptTemplate(template="From the provided text below, extract the key details of the job posting. Focus on the role title, required skills, qualifications, and a brief description. Return the information in a clean JSON format with keys: `role`, `skills`, `qualification`, and `description`. If a detail is not found, return null for that key. VALID JSON (NO PREAMBLE): \n {page_data}", input_variables=["page_data"])
        chain = prompt | llm | parser
        try: return chain.invoke({'page_data': text})
        except Exception as e: st.error(f"Failed to parse job details. Error: {e}"); return None

    def generate_email_content(job_details, resume_text):
        email_prompt = PromptTemplate(template="### RESUME DETAILS:\n{resume}\n\n### JOB DESCRIPTION:\n{job_desc}\n\n### INSTRUCTIONS:\nWrite a concise, engaging, and professional cold email (under 200 words). The tone should be warm, confident, and conversational. Directly address the recruiter. Seamlessly integrate skills from the resume relevant to the job. Do NOT use bullet points. Write in full paragraphs. Include a clear call to action. Ensure the final output is only the email content, with a professional closing. NO PREAMBLE.", input_variables=["resume", "job_desc"])
        chain = email_prompt | llm
        try: return chain.invoke({'resume': resume_text, 'job_desc': job_details}).content
        except Exception as e: st.error(f"Failed to generate email: {e}"); return None

    st.markdown("#### Job Details")
    input_method = st.radio("Provide Job Details via:", ("URL", "Text Description"), horizontal=True, key="email_input")
    job_text = None
    if input_method == "URL":
        url = st.text_input("Enter the URL of the job posting")
        if url: 
            with st.spinner("Fetching content..."): job_text = extract_text_from_url(url)
    else:
        job_text = st.text_area("Paste the job description here", height=250)

    if st.button("✨ Generate Email", use_container_width=True, type="primary"):
        if not job_text: st.warning("Please provide the job details.", icon="⚠️")
        else:
            with st.spinner("Analyzing job..."): job_details = get_job_details_from_text(job_text)
            if job_details:
                with st.spinner("Crafting email..."): email_content = generate_email_content(job_details, resume_text)
                if email_content:
                    st.markdown("#### Generated Cold Email:")
                    formatted_email = email_content.replace("\n", "<br>")
                    st.markdown(f'<div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">{formatted_email}</div>', unsafe_allow_html=True)


# --- TOOL: Skill Gap Analysis Functions ---
def skill_gap_tool():
    st.subheader("📊 Analyze Your Skill Gap")
    parser = JsonOutputParser()
    llm = get_llm()
    resume_text = st.session_state.get("resume_text")

    def extract_skills_from_resume(text: str):
        prompt = PromptTemplate(template="Analyze the resume text and extract all technical and soft skills. Return the skills as a JSON list of strings. Example: [\"Python\", \"Machine Learning\"].\n\nRESUME TEXT:\n{resume_text}\n\nVALID JSON (NO PREAMBLE):", input_variables=["resume_text"])
        chain = prompt | llm | parser
        try: return chain.invoke({'resume_text': text})
        except Exception: return []

    def get_required_skills_for_domain(domain: str):
        prompt = PromptTemplate(template="For the target job domain \"{domain}\", list the top 15 most essential skills. Return skills as a JSON list of strings. Example: [\"SQL\", \"Data Visualization\"].\n\nVALID JSON (NO PREAMBLE):", input_variables=["domain"])
        chain = prompt | llm | parser
        try: return chain.invoke({'domain': domain})
        except Exception: return []

    def get_skill_improvement_suggestions(missing_skills: list, domain: str):
        prompt = PromptTemplate(template="A user is targeting a job in \"{domain}\" and is missing the following skills: {skills}. For each missing skill, provide a brief, actionable suggestion on how to learn it (e.g., online courses, project ideas). Format as markdown.\n\nYOUR RESPONSE (MARKDOWN FORMAT, NO PREAMBLE):", input_variables=["skills", "domain"])
        chain = prompt | llm
        try: return chain.invoke({'skills': ", ".join(missing_skills), 'domain': domain}).content
        except Exception: return "Could not generate suggestions."

    target_domain = st.text_input("Enter your target job/domain (e.g., Data Scientist)")
    if st.button("Analyze Skill Gap", use_container_width=True, type="primary"):
        if resume_text and target_domain:
            with st.spinner("Analyzing your skills and target domain..."):
                resume_skills = extract_skills_from_resume(resume_text)
                required_skills = get_required_skills_for_domain(target_domain)
            if resume_skills and required_skills:
                resume_skills_lower = {skill.lower() for skill in resume_skills}
                required_skills_lower = {skill.lower() for skill in required_skills}
                missing_skills = sorted(list(required_skills_lower - resume_skills_lower))
                st.markdown("#### Analysis Complete!")
                col1, col2 = st.columns(2)
                with col1: st.success(f"**Skills You Have:** {', '.join(sorted(list(resume_skills_lower & required_skills_lower)))}")
                with col2:
                    if missing_skills: st.warning(f"**Skills to Acquire:** {', '.join(missing_skills)}")
                    else: st.balloons(); st.success("You have all the required skills!")
                if missing_skills:
                    with st.spinner("Generating learning plan..."):
                        suggestions = get_skill_improvement_suggestions(missing_skills, target_domain)
                        st.markdown("#### 🚀 Your Learning Plan")
                        st.markdown(suggestions)
        else: st.warning("Please enter a target domain.", icon="⚠️")

# --- TOOL: Resume Summary Functions ---
def resume_summary_tool():
    st.subheader("📄 Generate a Professional Resume Summary")
    llm = get_llm()
    resume_text = st.session_state.get("resume_text")
    
    def generate_resume_summary(text: str):
        prompt = PromptTemplate(template="Act as an expert career coach. Based on the resume text below, write a professional summary (150-200 words). Highlight key experiences, top skills, and significant achievements. The tone should be professional and confident. Structure it as a single paragraph.\n\nRESUME TEXT:\n{resume_text}\n\nPROFESSIONAL SUMMARY (NO PREAMBLE):", input_variables=["resume_text"])
        chain = prompt | llm
        try: return chain.invoke({'resume_text': text}).content
        except Exception as e: st.error(f"Failed to generate summary: {e}"); return None
        
    if st.button("✨ Generate Summary", use_container_width=True, type="primary"):
        if resume_text:
            with st.spinner("Analyzing and summarizing your resume..."): summary = generate_resume_summary(resume_text)
            if summary:
                st.markdown("#### Your Professional Summary")
                st.markdown(f'<div style="border: 2px solid #3498DB; border-radius: 10px; padding: 25px; background-color: #F5F5F5; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"><p style="font-size: 1.1rem; line-height: 1.6;">{summary}</p></div>', unsafe_allow_html=True)

# --- Main Application Logic ---
def main_app():
    """The main application interface shown after a successful login."""
    st.sidebar.success(f"Welcome, {st.session_state['username'].capitalize()}!")
    
    # Step 1: Handle Resume Upload
    if not st.session_state["resume_uploaded"]:
        st.header(f"Welcome {st.session_state['username'].capitalize()}!")
        resume_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])
        if resume_file:
            with st.spinner("Processing resume..."):
                extracted_text = get_resume_text(resume_file)
                if extracted_text:
                    st.session_state["resume_text"] = extracted_text
                    st.session_state["resume_uploaded"] = True
                    st.success("Resume uploaded!")
                    time.sleep(1); st.rerun()
                else: st.error("Failed to extract text from the resume.")
        st.markdown("""
                # 📄 Resume Summary, Skill Analysis & Email Creator

                Welcome to the **Resume Insight App** – a smart, AI-powered tool designed to make career tasks effortless.  
                This app helps you **summarize resumes**, **analyze skills**, and **generate professional emails** in just a few clicks.

                ---

                ## 🚀 Features

                ### 1️⃣ Resume Summary  
                Easily extract the most important details from a resume.  
                - AI-powered content extraction  
                - Highlighted **experience, education, and achievements**  
                - Short and concise professional summary  

                ### 2️⃣ Skill Gap Analysis  
                Identify **skills present** and **skills missing** based on a specific domain or job role.  
                - Match resume skills to industry requirements  
                - Get recommendations for **upskilling**  
                - Clear visualization of strengths & gaps  

                ### 3️⃣ Professional Email Creator  
                Craft high-quality, professional emails instantly.  
                - Job application emails  
                - Networking & follow-up templates  
                - Customizable tone & style  

                ---

                ## 💡 Why Use This App?
                - Saves hours of manual work  
                - Improves job application quality  
                - Provides **actionable career insights**  
                - Ensures professional communication  

                ---

                ### 🛠️ How to Use
                1. **Upload your resume** in PDF/DOCX format.  
                2. Select **Skill Analysis** or **Summary** options.  
                3. Generate a **custom email** for job applications.  

                ---

                🔹 *Empowering your career with AI-driven insights.*  
                """)
    
    # Step 2: Show Tools in Tabs once resume is uploaded
    else:
        st.title("AI Career Assistant Tools")        
        tab1, tab2, tab3 = st.tabs(["📄 Resume Summary", "📊 Skill Gap Analysis" ,"📧 Cold Email Generator"])

        with tab1:
            resume_summary_tool()  
        with tab2:
            skill_gap_tool()
            
        with tab3:
            email_generator_tool()

# --- Entry Point ---
if not st.session_state["logged_in"]:
    login_page()
else:
    main_app()