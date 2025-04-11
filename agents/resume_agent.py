from autogen import AssistantAgent
from utils.extract import extract_text_from_pdf, extract_text_from_docx
import re

resume_agent = AssistantAgent(
    name="Resume_Agent",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "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"}]},
    system_message="You extract structured data (name, email, skills, etc.) from uploaded resumes."
)

@resume_agent.register_for_execution()
def parse_resumes(summary: dict):
    resumes = summary.get("resumes", [])
    parsed_resumes = []

    for file in resumes:
        if file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            text = extract_text_from_docx(file)
        else:
            continue

        name_match = re.search(r"(?i)name:?\s*(.*)", text)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
        skills_match = re.findall(r"(?i)(?:skills|technologies):?\s*(.*)", text)
        experience_match = re.findall(r"(?i)(\d+\+? years.*?)\n", text)
        qualifications_match = re.findall(r"(?i)(Bachelor's|Master's|PhD)[^\n]*", text)
        title_match = re.findall(r"(?i)(?:title|position):?\s*(.*)", text)

        parsed = {
            "name": name_match.group(1).strip() if name_match else "Unknown",
            "email": email_match.group() if email_match else "unknown@example.com",
            "job_title": title_match[0] if title_match else "",
            "skills": skills_match[0].split(",") if skills_match else [],
            "experience": experience_match,
            "qualifications": qualifications_match
        }

        parsed_resumes.append(parsed)

    summary["parsed_resumes"] = parsed_resumes
    return summary
