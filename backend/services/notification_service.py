"""
FIREGUARD AI - NotificationService (Requirement 16)
Orchestrates multi-channel notifications (SMS, Email, Push) with mock and live provider support.
"""
from typing import Dict, Any, List
from backend.integrations.notification_providers import get_notification_provider

class NotificationService:
    """Service broadcasting tactical alerts across communication channels."""

    @staticmethod
    def dispatch_alert(
        alert_title: str,
        alert_message: str,
        channels: List[str],
        recipient_phone: str = "+91 98765 43210",
        recipient_email: str = "emergency.command@fireguard.gov.in"
    ) -> Dict[str, Any]:
        """Dispatches notification to requested channels."""
        provider = get_notification_provider()
        results = {}

        if "SMS" in channels:
            results["sms"] = provider.send_sms(recipient_phone, f"{alert_title}: {alert_message}")

        if "EMAIL" in channels:
            results["email"] = provider.send_email(recipient_email, alert_title, alert_message)

        if "PUSH" in channels or "DASHBOARD" in channels:
            results["push"] = provider.send_push("TACTICAL_INCIDENTS", alert_title, alert_message)

        return {
            "success": True,
            "dispatched_channels": channels,
            "provider_audit": results
        }
