from autogen import AssistantAgent
from utils.email_utils import send_email, generate_email

email_agent = AssistantAgent(
    name="Email_Agent",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "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"}]},
    system_message="You generate and send interview invitation emails to shortlisted candidates."
)

@email_agent.register_for_execution()
def notify_candidates(summary: dict):
    sender_email = summary.get("sender_email")
    sender_password = summary.get("sender_password")
    selected_date = summary.get("selected_date")
    selected_time = summary.get("selected_time")
    matched_resumes = summary.get("matched_resumes", [])

    notifications = []

    for candidate in matched_resumes:
        if candidate.get("status") == "Shortlisted":
            cal_link = candidate.get("calendar_link", "")
            body = generate_email(
                candidate["name"],
                candidate["match_score"],
                selected_date,
                selected_time,
                cal_link
            )
            success = send_email(
                candidate["email"],
                "Interview Invitation",
                body,
                sender_email,
                sender_password
            )
            notifications.append({
                "email": candidate["email"],
                "sent": success
            })

    summary["notifications"] = notifications
    return summary
