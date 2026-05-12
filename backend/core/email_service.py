import os
import requests
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

# Transactional Email configuration
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "RESEND") # RESEND, SENDGRID, or MOCK
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "support@hyper-saas.com")

class EmailService:
    @staticmethod
    async def send_email(to: str, subject: str, html_content: str):
        """Sends a transactional email using the configured provider."""
        if EMAIL_PROVIDER == "MOCK" or not EMAIL_API_KEY:
            print(f"MOCK EMAIL to {to}: {subject}")
            return {"status": "mock_sent"}

        if EMAIL_PROVIDER == "RESEND":
            return await EmailService._send_resend(to, subject, html_content)
        elif EMAIL_PROVIDER == "SENDGRID":
            return await EmailService._send_sendgrid(to, subject, html_content)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid email provider: {EMAIL_PROVIDER}")

    @staticmethod
    async def _send_resend(to: str, subject: str, html_content: str):
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {EMAIL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "from": FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html_content
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    @staticmethod
    async def _send_sendgrid(to: str, subject: str, html_content: str):
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {EMAIL_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": FROM_EMAIL},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_content}]
        }
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code not in [200, 201, 202]:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return {"status": "sent"}

email_service = EmailService()
