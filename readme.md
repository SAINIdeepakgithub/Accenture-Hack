
# Multi-Agent Resume Screening System

An AI-powered resume screening platform developed for the Accenture Hackathon. This Streamlit-based web application allows users to upload resumes and job descriptions, automatically computes match scores, schedules interviews through Google Calendar, and sends interview invites to shortlisted candidates via email.

## Features

- Upload multiple resumes (PDF or DOCX formats)
- Parse job descriptions and resumes using pattern-based extraction
- Compute semantic similarity using Sentence Transformers
- Automatically shortlist candidates based on a threshold
- Schedule interviews using Google Calendar API
- Send email notifications to shortlisted candidates
- Persist candidate data in a local SQLite database

## Folder Structure

```
accenture-hack/
│
├── resume/
│   ├── main.py                  # Main Streamlit application
│   ├── token.json               # Google Calendar OAuth token
│   ├── credentials.json         # Google Calendar API credentials
│   ├── candidates.db            # SQLite database file
│   └── venv/                    # Python virtual environment
│
└── README.md                    # Project documentation
```

## Technologies Used

- Python 3.x
- Streamlit
- Sentence Transformers (all-MiniLM-L6-v2)
- SQLite
- Google Calendar API
- SMTP (Gmail)
- PyPDF2, docx2txt
- Regular Expressions (regex)

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/accenture-hack.git
   cd accenture-hack/resume
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Calendar API
   - Download your `credentials.json` from Google Cloud Console
   - Place it in the `resume/` folder

5. Run the application
   ```bash
   streamlit run main.py
   ```

## Test Email Configuration

For testing purposes, the application can send emails using the following credentials:

- Sender Email: foronlinecourses05@gmail.com
- App Password: hzrd bxgi gvfq qhzg

These credentials are used to send automated interview invites to shortlisted candidates. Store them securely or use environment variables in production.

## License

This project is for educational and demonstration purposes only. Not intended for production use without additional security and compliance considerations.
