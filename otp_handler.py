import random
import smtplib
from email.mime.text import MIMEText
from config import SENDER_EMAIL, APP_PASSWORD


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(receiver_email, otp):
    subject = "Student Tech - Your OTP Code"
    body = f"Your OTP code is: {otp}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False
