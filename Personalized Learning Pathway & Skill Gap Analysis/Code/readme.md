Setup and Installation 🚀
Follow these steps to get the application running on your local machine.


pip install -r requirements.txt
1. Set Up Environment Variables
The application requires an API key from Groq to use its LLM services.

Add your Groq API key to this  **utils.py** file as follows:

GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
You can obtain a free API key from the GroqCloud Webpage.

How to Run the Application ▶️
Once the setup is complete, you can run the Streamlit application with a single command:

streamlit run app.py
Your web browser should automatically open to the application's login page.

Usage Guide 📖
Login: Use the credentials user / pass or demo / streamlit to log in.

Upload Resume: After logging in, you will be prompted to upload your resume. This is a one-time step for your session.

Select a Tool: Once your resume is uploaded, the main tools will appear in a tabbed interface.

Cold Email Generator: Choose an input method (URL or Text), provide the job details, and click "Generate Email."

Skill Gap Analysis: Enter your target job title (e.g., "Software Engineer") and click "Analyze Skill Gap."

Resume Summary: Simply click "Generate Summary" to get a professional summary of your uploaded resume.