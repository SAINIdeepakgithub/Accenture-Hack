from autogen import AssistantAgent
from utils.calendar_utils import create_event

schedule_agent = AssistantAgent(
    name="Schedule_Agent",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "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"}]},
    system_message="You schedule interviews on Google Calendar and return calendar event links."
)

@schedule_agent.register_for_execution()
def schedule_interviews(summary: dict):
    matched_resumes = summary.get("matched_resumes", [])
    selected_date = summary.get("selected_date")
    selected_time = summary.get("selected_time")

    for candidate in matched_resumes:
        if candidate.get("status") == "Shortlisted":
            link = create_event(
                summary=f"Interview with {candidate['name']}",
                date=selected_date,
                time=selected_time,
                attendee_email=candidate["email"]
            )
            candidate["calendar_link"] = link

    summary["matched_resumes"] = matched_resumes
    return summary
