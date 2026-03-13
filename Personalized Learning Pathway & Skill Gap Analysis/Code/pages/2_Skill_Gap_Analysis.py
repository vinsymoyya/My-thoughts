import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils import get_llm

# --- Page Setup ---
st.set_page_config(page_title="Skill Gap Analysis", layout="wide")
st.title("📊 Skill Gap Analysis")
st.markdown("Identify the skills you need to land your dream job.")

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
def extract_skills_from_resume(text: str):
    prompt = PromptTemplate(template="Analyze the resume text and extract all technical and soft skills. Return the skills as a JSON list of strings. Example: [\"Python\", \"Machine Learning\", \"Communication\"].\n\nRESUME TEXT:\n{resume_text}\n\nVALID JSON (NO PREAMBLE):", input_variables=["resume_text"])
    chain = prompt | llm | parser
    try:
        return chain.invoke({'resume_text': text})
    except Exception: return []

def get_required_skills_for_domain(domain: str):
    prompt = PromptTemplate(template="For the target job domain \"{domain}\", list the top 15 most essential skills. Return the skills as a JSON list of strings. Example: [\"SQL\", \"Data Visualization\", \"Problem Solving\"].\n\nVALID JSON (NO PREAMBLE):", input_variables=["domain"])
    chain = prompt | llm | parser
    try:
        return chain.invoke({'domain': domain})
    except Exception: return []

def get_skill_improvement_suggestions(missing_skills: list, domain: str):
    prompt = PromptTemplate(template="A user is targeting a job in \"{domain}\" and is missing the following skills: {skills}. For each missing skill, provide a brief, actionable suggestion on how to learn it (e.g., online courses, project ideas). Format as markdown.\n\nYOUR RESPONSE (MARKDOWN FORMAT, NO PREAMBLE):", input_variables=["skills", "domain"])
    chain = prompt | llm
    try:
        return chain.invoke({'skills': ", ".join(missing_skills), 'domain': domain}).content
    except Exception: return "Could not generate suggestions."

# --- UI Layout ---
st.info("Specify your target job domain to see what skills you should focus on.", icon="💡")

target_domain = st.text_input("Enter your target job/domain (e.g., Data Scientist, Backend Developer)")

if st.button("Analyze Skill Gap", use_container_width=True, type="primary"):
    if resume_text and target_domain:
        with st.spinner("Analyzing your resume and target domain..."):
            resume_skills = extract_skills_from_resume(resume_text)
            required_skills = get_required_skills_for_domain(target_domain)
        
        if resume_skills and required_skills:
            resume_skills_lower = {skill.lower() for skill in resume_skills}
            required_skills_lower = {skill.lower() for skill in required_skills}
            missing_skills = sorted(list(required_skills_lower - resume_skills_lower))
            
            st.header("Analysis Complete!")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✅ Skills You Have")
                st.success(", ".join(sorted(list(resume_skills_lower & required_skills_lower))))
            with col2:
                st.subheader("🎯 Skills to Acquire")
                if missing_skills:
                    st.warning(", ".join(missing_skills))
                else:
                    st.balloons()
                    st.success("You have all the required skills! Great job!")
            if missing_skills:
                with st.spinner("Generating learning suggestions..."):
                    suggestions = get_skill_improvement_suggestions(missing_skills, target_domain)
                    st.header("🚀 Your Learning Plan")
                    st.markdown(suggestions)
    else:
        st.warning("Please enter a target domain.", icon="⚠️")