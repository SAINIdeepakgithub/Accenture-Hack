import streamlit as st
from agents.jd_agent import jd_agent
from agents.resume_agent import resume_agent
from agents.matcher_agent import matcher_agent
from agents.schedule_agent import schedule_agent
from agents.email_agent import email_agent
from autogen import UserProxyAgent, GroupChat, GroupChatManager
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env vars
from autogen import UserProxyAgent
llm_config = {
    "config_list": [
        {
            "model": "gpt-4",  # or "gpt-3.5-turbo"
            "api_key": os.getenv("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")
        }
    ],
    "cache_seed": 42,
}


# Streamlit UI
st.title("🤖 AutoGen Resume Screening System")

jd_text = st.text_area("Paste Job Description")
resumes = st.file_uploader("Upload Resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
sender_email = st.text_input("SMTP Email")
sender_password = st.text_input("SMTP App Password", type="password")
thresh = st.slider("Match Threshold (%)", 0, 100, 80)
date = st.date_input("Interview Date")
time = st.selectbox("Interview Time", ["10:00", "14:00", "16:30"])

if st.button("Run ATS"):
    if jd_text and resumes:
        # Wrap user input into one summary dict
        summary = {
            "jd_text": jd_text,
            "resumes": resumes,
            "threshold": thresh,
            "selected_date": str(date),
            "selected_time": time,
            "sender_email": sender_email,
            "sender_password": sender_password
        }

        # Define user
        user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        is_termination_msg=lambda x: x.get("name") == "Email_Agent",
        code_execution_config={"use_docker": False},  # <--- important
        llm_config=llm_config
        )


        # Group Chat
        chat = GroupChat(agents=[user_proxy, jd_agent, resume_agent, matcher_agent, schedule_agent, email_agent], messages=[])
        manager = GroupChatManager(groupchat=chat, llm_config={"config_list": [{"model": "gpt-4", "api_key": "your-api-key"}]})

        # Start execution
        user_proxy.initiate_chat(manager, message=summary)
        st.success("✅ Multi-agent ATS process completed!")
