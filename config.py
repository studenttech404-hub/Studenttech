# config.py

import os

# Email credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "studenttech404@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "oata xwjd slng xmqq")

# Optional: you can keep SENDER_EMAIL if you like
SENDER_EMAIL = EMAIL_ADDRESS
APP_PASSWORD = EMAIL_PASSWORD