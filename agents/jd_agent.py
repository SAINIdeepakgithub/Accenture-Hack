from autogen import AssistantAgent
import re

jd_agent = AssistantAgent(
    name="JD_Agent",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "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"}]},
    system_message="You are an assistant who extracts job role, skills, experience, and qualifications from a job description."
)

@jd_agent.register_for_execution()
def parse_jd(summary: dict):
    text = summary.get("jd_text", "")
    skills = re.findall(r"(?i)(?:skills required|skills include|proficient in|experience with):?\s*(.*)", text)
    experience = re.findall(r"(?i)(\d+\+? years.*?)\n", text)
    qualifications = re.findall(r"(?i)(Bachelor's|Master's|PhD)[^\n]*", text)
    title = re.findall(r"(?i)Title:?\s*(.*)", text)

    parsed = {
        "job_title": title[0] if title else "",
        "required_skills": skills[0].split(",") if skills else [],
        "experience": experience,
        "qualifications": qualifications
    }
    summary["jd_summary"] = parsed
    return summary
