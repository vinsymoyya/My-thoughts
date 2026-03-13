import streamlit as st
from langchain_core.prompts import PromptTemplate
from utils import get_llm

# --- Page Setup ---
st.set_page_config(page_title="Resume Summary", layout="wide")
st.title("📄 Resume Summary Generator")
st.markdown("Get a concise, professional summary of your resume in seconds.")

# --- Authentication & Resume Check ---
if not st.session_state.get("logged_in"):
    st.warning("Please log in first to access this page.")
    st.stop()
if not st.session_state.get("resume_text"):
    st.warning("Please upload your resume on the 'Home' page first to use this tool.")
    st.stop()

# --- Initialization ---
llm = get_llm()
resume_text = st.session_state.get("resume_text")

# --- Helper Function for This Page ---
def generate_resume_summary(text: str):
    """Uses LLM to generate a professional summary of the resume."""
    prompt = PromptTemplate(
        template="""Act as an expert career coach. Based on the resume text below, write a professional summary. The summary should be concise, powerful, and between 150-200 words. Highlight key experiences, top skills, and significant achievements. The tone should be professional and confident. Structure it as a single paragraph.\n\nRESUME TEXT:\n{resume_text}\n\nPROFESSIONAL SUMMARY (NO PREAMBLE):""",
        input_variables=["resume_text"],
    )
    chain = prompt | llm
    try:
        response = chain.invoke({'resume_text': text})
        return response.content
    except Exception as e:
        st.error(f"Failed to generate summary: {e}")
        return None

# --- UI Layout ---
st.info("Click the button below to generate a professional summary based on your uploaded resume.", icon="💡")

if st.button("✨ Generate Summary", use_container_width=True, type="primary"):
    if resume_text:
        with st.spinner("Reading and analyzing your resume..."):
            summary = generate_resume_summary(resume_text)
        
        if summary:
            st.subheader("Your Professional Summary")
            st.markdown(
                f"""
                <div style="border: 2px solid #3498DB; border-radius: 10px; padding: 25px; background-color: #F5F5F5; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    <p style="font-size: 1.1rem; line-height: 1.6;">{summary}</p>
                </div>
                """,
                unsafe_allow_html=True
            )