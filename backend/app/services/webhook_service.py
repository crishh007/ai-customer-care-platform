import asyncio
from datetime import datetime

class WebhookService:
    """
    Mock service to simulate sending notifications to external systems like Slack or Email.
    In a real production environment, this would use `httpx` or `requests` to hit actual APIs.
    """
    
    @staticmethod
    async def send_slack_alert(message: str, channel: str = "#escalations"):
        """Simulate sending a Slack message"""
        print(f"\n[WEBHOOK TRIGGERED - SLACK] {datetime.now()}")
        print(f"Channel: {channel}")
        print(f"Payload: {message}")
        print("Status: 200 OK (Mocked)\n")
        # Simulate network latency
        await asyncio.sleep(0.5)
        return True

    @staticmethod
    async def send_email_alert(to_email: str, subject: str, body: str):
        """Simulate sending an Email via SendGrid/SES"""
        print(f"\n[WEBHOOK TRIGGERED - EMAIL] {datetime.now()}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        print("Status: 202 Accepted (Mocked)\n")
        # Simulate network latency
        await asyncio.sleep(0.5)
        return True
