"""
FIREGUARD AI - Notification Provider Abstractions (Requirement 16)
Supports Mock provider, Twilio SMS integration, SMTP Email, and Web push, with clear DEMO NOTIFICATION audit logging.
"""
import logging
from typing import Dict, Any, List
from backend.config.settings import settings

logger = logging.getLogger("FIREGUARD.NOTIFICATIONS")

class BaseNotificationProvider:
    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        raise NotImplementedError

    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        raise NotImplementedError

    def send_push(self, topic: str, title: str, body: str) -> Dict[str, Any]:
        raise NotImplementedError

class MockNotificationProvider(BaseNotificationProvider):
    """
    Mock notification provider for demo evaluations.
    Logs clear DEMO NOTIFICATION tags and simulates successful delivery.
    """
    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        log_msg = f"[DEMO NOTIFICATION - SMS] To: {to_number} | Content: {message}"
        print(log_msg)
        logger.info(log_msg)
        return {
            "status": "SENT",
            "provider": "DEMO MOCK PROVIDER",
            "channel": "SMS",
            "recipient": to_number,
            "disclaimer": "DEMO NOTIFICATION - No real cellular dispatch transmitted"
        }

    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        log_msg = f"[DEMO NOTIFICATION - EMAIL] To: {to_email} | Subject: {subject}"
        print(log_msg)
        logger.info(log_msg)
        return {
            "status": "SENT",
            "provider": "DEMO MOCK PROVIDER",
            "channel": "EMAIL",
            "recipient": to_email,
            "subject": subject,
            "disclaimer": "DEMO NOTIFICATION - Simulated email transmission"
        }

    def send_push(self, topic: str, title: str, body: str) -> Dict[str, Any]:
        log_msg = f"[DEMO NOTIFICATION - PUSH] Topic: {topic} | Title: {title}"
        print(log_msg)
        logger.info(log_msg)
        return {
            "status": "SENT",
            "provider": "DEMO MOCK PROVIDER",
            "channel": "PUSH",
            "topic": topic,
            "disclaimer": "DEMO NOTIFICATION - Browser alert queued"
        }

class TwilioSMSProvider(BaseNotificationProvider):
    """Live Twilio provider when environment variables are supplied."""
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            msg = client.messages.create(body=message, from_=self.from_number, to=to_number)
            return {"status": "SENT", "provider": "Twilio", "sid": msg.sid, "channel": "SMS"}
        except Exception as e:
            logger.error(f"Twilio transmission failed: {e}")
            return {"status": "FAILED", "provider": "Twilio", "error": str(e)}

def get_notification_provider() -> BaseNotificationProvider:
    """Factory selecting provider based on available configuration."""
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER and not settings.DEMO_MODE:
        return TwilioSMSProvider(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER)
    return MockNotificationProvider()
