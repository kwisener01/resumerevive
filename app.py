import streamlit as st
from openai import OpenAI
import docx2txt
import PyPDF2
import tempfile
from docx import Document
from datetime import datetime

# --- CONFIG ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # Put your OpenAI API key in Streamlit secrets

# --- FUNCTIONS ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    return docx2txt.process(tmp_path)

def generate_resume(job_description, resume_text):
    prompt = f"""
You are a world-class resume coach. Please tailor the following resume to the job description provided. 
Your goal is to align the resume to key responsibilities and skills, optimize for ATS readability, and keep the tone professional and natural. Use a clean format and keep it under two pages.

Job Description:
{job_description}

Original Resume:
{resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

def save_to_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    file_path = f"Kevin_ResumeRevive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(file_path)
    return file_path

# --- UI ---
st.title("📄 ResumeRevive AI")
st.write("Tailor your resume to any job using GPT-4")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
job_description = st.text_area("Paste the job description here")

if uploaded_file and job_description:
    file_type = uploaded_file.name.split(".")[-1]

    if file_type == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_type == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Unsupported file type")
        st.stop()

    if st.button("Generate Tailored Resume"):
        with st.spinner("Generating with GPT-4..."):
            tailored_resume = generate_resume(job_description, resume_text)
            docx_path = save_to_docx(tailored_resume)

        st.success("✅ Resume tailored successfully!")
        st.download_button("📥 Download Resume", data=open(docx_path, "rb"), file_name=docx_path, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
