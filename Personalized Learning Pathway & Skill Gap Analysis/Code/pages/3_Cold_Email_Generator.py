import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils import get_llm, extract_text_from_url

# --- Page Setup ---
st.set_page_config(page_title="Cold Email Generator", layout="wide")
st.title("📮 Cold Email Generator")
st.markdown("Craft a professional and personalized email to recruiters in seconds!")

# --- Authentication & Resume Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in first to access this page.")
    st.stop()
if not st.session_state.get("resume_text"):
    st.warning("Please upload your resume on the 'Home' page first to use this tool.")
    st.stop()

# --- Initialization ---
llm = get_llm()
parser = JsonOutputParser()
resume_text = st.session_state.get("resume_text")

# --- Helper Functions for This Page ---
def get_job_details_from_text(text: str):
    """Uses LLM to extract structured job details from raw text."""
    prompt = PromptTemplate(
        template="""From the provided text below, extract the key details of the job posting. Focus on the role title, required skills, qualifications, and a brief description. Return the information in a clean JSON format with keys: `role`, `skills`, `qualification`, and `description`. If a detail is not found, return null for that key. VALID JSON (NO PREAMBLE): \n {page_data}""",
        input_variables=["page_data"],
    )
    chain = prompt | llm | parser
    try:
        return chain.invoke({'page_data': text})
    except Exception as e:
        st.error(f"Failed to parse job details. Error: {e}")
        return None

def generate_email_content(job_details, resume_text):
    """Generates the email content using the LLM."""
    email_prompt = PromptTemplate(
        template="""### RESUME DETAILS:\n{resume}\n\n### JOB DESCRIPTION:\n{job_desc}\n\n### INSTRUCTIONS:\nWrite a concise, engaging, and professional cold email (under 200 words). The tone should be warm, confident, and conversational. Directly address the recruiter (e.g., "Dear Hiring Manager,"). Seamlessly integrate skills and experiences from the resume that are highly relevant to the job description. Do NOT use bullet points. Write in full paragraphs. Include a clear call to action (e.g., suggesting a brief chat). Ensure the final output is only the email content, with a professional closing. NO PREAMBLE.""",
        input_variables=["resume", "job_desc"],
    )
    chain = email_prompt | llm
    try:
        response = chain.invoke({'resume': resume_text, 'job_desc': job_details})
        return response.content
    except Exception as e:
        st.error(f"Failed to generate email: {e}")
        return None

# --- UI Layout ---
st.header("Job Details")
input_method = st.radio("Provide Job Details via:", ( "Text Description"), horizontal=True)

job_text = None
if input_method == "URL":
    url = st.text_input("Enter the URL of the job posting")
    if url:
        with st.spinner("Fetching content from URL..."):
            job_text = extract_text_from_url(url)
else:
    job_text = st.text_area("Paste the job description here", height=250)

# --- Email Generation Logic ---
if st.button("✨ Generate Email", use_container_width=True, type="primary"):
    if not job_text:
        st.warning("Please provide the job details (URL or text).", icon="⚠️")
    else:
        with st.spinner("Analyzing job description..."):
            job_details = get_job_details_from_text(job_text)
        
        if job_details:
            with st.spinner("Crafting the perfect email..."):
                email_content = generate_email_content(job_details, resume_text)
            
            if email_content:
                st.subheader("Generated Cold Email:")
                # CORRECTED LINE: Replaces the newline character \n with <br> for proper HTML rendering.
                formatted_email = email_content.replace("\n", "<br>")
                st.markdown(
                    f'<div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">{formatted_email}</div>',
                    unsafe_allow_html=True
                )