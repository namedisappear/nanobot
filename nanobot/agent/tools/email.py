"""Email tools for sending emails via SMTP."""

import smtplib
import ssl
from email.message import EmailMessage
from typing import Any

from loguru import logger

from nanobot.agent.tools.base import Tool
from nanobot.config.schema import EmailConfig


class SendEmailTool(Tool):
    """Tool for sending emails via SMTP."""

    def __init__(self, config: EmailConfig):
        self.config = config

    @property
    def name(self) -> str:
        return "send_email"

    @property
    def description(self) -> str:
        return (
            "Send an email to a specific address using the configured SMTP server. "
            "RESTRICTED: This tool is ONLY for the 'email' agent. "
            "If you are on a different channel (e.g. 'feishu'), you MUST use 'send_to_channel_agent' to ask the 'email' agent to do this. "
            "DO NOT use this tool directly from other channels."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "The recipient's email address (e.g. 'user@example.com')",
                },
                "subject": {
                    "type": "string",
                    "description": "The subject of the email",
                },
                "body": {
                    "type": "string",
                    "description": "The content/body of the email",
                },
            },
            "required": ["to", "subject", "body"],
        }

    async def execute(self, to: str, subject: str, body: str, **kwargs: Any) -> str:
        """Execute the email sending."""
        if not self.config.consent_granted:
            return "Error: Email sending is disabled because 'consent_granted' is false in configuration."

        if not self.config.smtp_host:
            return "Error: SMTP host is not configured."

        if not self.config.enabled:
             # Even if the channel is disabled for polling, we might want to allow sending if config is present?
             # Usually 'enabled' controls the channel loop. But let's check config.
             pass

        # Validate recipient
        to = to.strip()
        if not to or "@" not in to:
            return f"Error: Invalid recipient address '{to}'."

        email_msg = EmailMessage()
        # Fallback to smtp/imap username if from_address is not set
        from_addr = (
            self.config.from_address
            or self.config.smtp_username
            or self.config.imap_username
        )
        email_msg["From"] = from_addr
        email_msg["To"] = to
        email_msg["Subject"] = subject
        email_msg.set_content(body)

        try:
            self._smtp_send(email_msg)
            return f"Email sent successfully to {to}."
        except Exception as e:
            logger.error("Error sending email via tool: {}", e)
            return f"Error sending email: {e}"

    def _smtp_send(self, msg: EmailMessage) -> None:
        """Send email via SMTP (synchronous)."""
        timeout = 30
        if self.config.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                self.config.smtp_host,
                self.config.smtp_port,
                timeout=timeout,
            ) as smtp:
                if self.config.smtp_username and self.config.smtp_password:
                    smtp.login(self.config.smtp_username, self.config.smtp_password)
                smtp.send_message(msg)
            return

        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port, timeout=timeout) as smtp:
            if self.config.smtp_use_tls:
                smtp.starttls(context=ssl.create_default_context())
            if self.config.smtp_username and self.config.smtp_password:
                smtp.login(self.config.smtp_username, self.config.smtp_password)
            smtp.send_message(msg)
