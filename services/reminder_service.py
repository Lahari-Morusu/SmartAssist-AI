import os
import smtplib
from email.message import EmailMessage


# =========================
# EMAIL MESSAGE
# =========================
def build_reminder_message(task, due_at):
    return f"⏰ Reminder\n\nTask: {task}\nDue: {due_at}"


# =========================
# SMTP CONFIG
# =========================
def get_smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("SMTP_FROM_EMAIL"),
    }


# =========================
# EMAIL SENDER
# =========================
def send_email_reminder(task, due_at, contact):
    config = get_smtp_config()

    if not all([config["username"], config["password"], contact]):
        return {"sent": False, "reason": "Missing SMTP config"}

    try:
        msg = EmailMessage()
        msg["Subject"] = f"SmartAssist Reminder: {task}"
        msg["From"] = config["from_email"]
        msg["To"] = contact
        msg.set_content(build_reminder_message(task, due_at))

        with smtplib.SMTP(config["host"], config["port"]) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)

        print("EMAIL SENT SUCCESSFULLY")

        return {"sent": True, "method": "email"}

    except Exception as e:
        print("EMAIL ERROR:", e)
        return {"sent": False, "reason": str(e)}


# =========================
# MAIN FUNCTION (USED BY YOUR APP)
# =========================
def send_reminder(task, due_at, contact):
    return send_email_reminder(task, due_at, contact)
    