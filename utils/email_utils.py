import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
