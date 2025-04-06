# multiagent_resume_ats.py

import streamlit as st
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
import re
import datetime
from datetime import datetime as dt, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import docx2txt
import os

# Load model
model = SentenceTransformer('./local_model')

# Google Calendar Scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_event(summary, date, time, attendee_email):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    start_time_str = f"{date}T{time}:00"
    start_time = dt.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    end_time = start_time + timedelta(minutes=30)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'attendees': [{'email': attendee_email}],
        'reminders': {'useDefault': True}
    }

    event = service.events().insert(calendarId='primary', body=event, sendUpdates="all").execute()
    return event.get('htmlLink')


# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            match_score REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Insert candidate into DB
def insert_candidate(name, email, score, status):
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute("INSERT INTO candidates (name, email, match_score, status) VALUES (?, ?, ?, ?)",
              (name, email, score, status))
    conn.commit()
    conn.close()

# Extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# Extract text from DOCX
def extract_text_from_docx(file):
    with open("temp_resume.docx", "wb") as f:
        f.write(file.read())
    text = docx2txt.process("temp_resume.docx")
    os.remove("temp_resume.docx")
    return text

# Realistic JD and resume parsers using regex (basic heuristic parsing)
def parse_jd(text):
    skills = re.findall(r"(?i)(?:skills required|skills include|proficient in|experience with):?\s*(.*)", text)
    experience = re.findall(r"(?i)(\d+\+? years.*?)\n", text)
    qualifications = re.findall(r"(?i)(Bachelor's|Master's|PhD)[^\n]*", text)
    title = re.findall(r"(?i)Title:?\s*(.*)", text)

    return {
        "job_title": title[0] if title else "",
        "required_skills": skills[0].split(",") if skills else [],
        "experience": experience,
        "qualifications": qualifications
    }

def parse_resume(text):
    name_match = re.search(r"(?i)name:?\s*(.*)", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    skills_match = re.findall(r"(?i)(?:skills|technologies):?\s*(.*)", text)
    experience_match = re.findall(r"(?i)(\d+\+? years.*?)\n", text)
    qualifications_match = re.findall(r"(?i)(Bachelor's|Master's|PhD)[^\n]*", text)
    title_match = re.findall(r"(?i)(?:title|position):?\s*(.*)", text)

    return {
        "name": name_match.group(1).strip() if name_match else "Unknown",
        "email": email_match.group() if email_match else "unknown@example.com",
        "job_title": title_match[0] if title_match else "",
        "skills": skills_match[0].split(",") if skills_match else [],
        "experience": experience_match,
        "qualifications": qualifications_match
    }

# Calculate match
def calculate_match(jd_summary, resume_data):
    jd_skill_text = ", ".join(jd_summary.get("required_skills", []))
    resume_skill_text = ", ".join(resume_data.get("skills", []))

    jd_exp_text = " ".join(jd_summary.get("experience", []))
    resume_exp_text = " ".join(resume_data.get("experience", []))

    jd_qual_text = " ".join(jd_summary.get("qualifications", []))
    resume_qual_text = " ".join(resume_data.get("qualifications", []))

    jd_title = jd_summary.get("job_title", "")
    resume_title = resume_data.get("job_title", "")

    skill_emb = util.cos_sim(model.encode([jd_skill_text])[0], model.encode([resume_skill_text])[0]).item()
    exp_emb = util.cos_sim(model.encode([jd_exp_text])[0], model.encode([resume_exp_text])[0]).item()
    qual_emb = util.cos_sim(model.encode([jd_qual_text])[0], model.encode([resume_qual_text])[0]).item()
    title_emb = util.cos_sim(model.encode([jd_title])[0], model.encode([resume_title])[0]).item()

    match_score = (
        0.5 * skill_emb +
        0.2 * exp_emb +
        0.2 * qual_emb +
        0.1 * title_emb
    ) * 100
    return round(match_score, 2)

# Generate email
def generate_email(name, score, selected_date, selected_time, calendar_link):
    return f"""
Subject: Interview Invitation for Next Step in Recruitment

Dear {name},

Congratulations! Based on your resume evaluation, you have been shortlisted with a match score of {score}%.

We’d love to invite you for an interview.

📅 Date: {selected_date}  
🕒 Time: {selected_time}  
💻 Format: Online (Zoom/Google Meet)  
📅 Calendar Event: {calendar_link}

Please confirm your availability. We look forward to speaking with you!

Best regards,  
Recruitment Team
"""

# Send email
def send_email(to_email, subject, body, sender_email, sender_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

# Streamlit App
init_db()
st.title("📄 AI-Powered Resume Screener")

st.header("💼 Job Description")
jd_input = st.text_area("Paste the Job Description")

st.header("📂 Upload Resumes")
resumes = st.file_uploader("Upload PDF or DOCX resumes", type=["pdf", "docx"], accept_multiple_files=True)

sender_email = st.text_input("Your Email (SMTP)")
sender_password = st.text_input("App Password (Hidden)", type="password")

threshold = st.slider("Match Threshold for Shortlisting (%)", min_value=0, max_value=100, value=80, step=1)

# Interview slot picker
st.header("🗓️ Interview Schedule Options")
today = datetime.date.today()
date_options = [today + datetime.timedelta(days=i) for i in range(1, 6)]
selected_date = st.selectbox("Select Interview Date", date_options)
selected_time = st.selectbox("Select Interview Time", ["10:00", "14:00", "16:30"])

if st.button("Run Matching") and jd_input and resumes:
    jd_summary = parse_jd(jd_input)
    for resume_file in resumes:
        if resume_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(resume_file)
        elif resume_file.name.endswith(".docx"):
            text = extract_text_from_docx(resume_file)
        else:
            st.warning(f"Unsupported file format: {resume_file.name}")
            continue

        resume_data = parse_resume(text)
        score = calculate_match(jd_summary, resume_data)
        status = "Shortlisted" if score >= threshold else "Rejected"
        insert_candidate(resume_data['name'], resume_data['email'], score, status)

        st.write(f"**{resume_data['name']}**: {score}% match ({status})")

        if status == "Shortlisted":
            cal_link = create_event(f"Interview with {resume_data['name']}", selected_date.isoformat(), selected_time, resume_data['email'])
            email_body = generate_email(resume_data['name'], score, selected_date, selected_time, cal_link)
            if send_email(resume_data['email'], "Interview Invitation", email_body, sender_email, sender_password):
                st.success(f"✅ Email sent to {resume_data['email']}")
            else:
                st.error(f"❌ Failed to send email to {resume_data['email']}")
