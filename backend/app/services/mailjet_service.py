"""Mailjet campaign draft helper."""
from __future__ import annotations

from typing import Dict, Optional

try:
    from mailjet_rest import Client as MailjetClient
except Exception:  # pragma: no cover
    MailjetClient = None  # type: ignore

from ..config import get_settings
from ..logger import get_logger

logger = get_logger(__name__)


class MailjetService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[MailjetClient] = None
        if self.settings.mailjet_api_key and self.settings.mailjet_api_secret:
            if MailjetClient is None:
                raise RuntimeError("mailjet_rest is not installed but credentials provided")
            self._client = MailjetClient(
                auth=(self.settings.mailjet_api_key, self.settings.mailjet_api_secret)
            )
        else:
            logger.warning("mailjet.disabled", reason="missing credentials")

    def create_draft(self, subject: str, preheader: str, html: str, text: str) -> Dict[str, str]:
        if not self._client:
            logger.info("mailjet.mock_draft", subject=subject)
            return {"DraftID": "mock", "Status": "saved"}
        draft_response = self._client.campaigndraft.create(
            data={
                "Locale": "en_US",
                "Sender": self.settings.mailjet_sender_name,
                "SenderEmail": self.settings.mailjet_sender_email,
                "Subject": subject,
                "ContactsListID": self.settings.mailjet_contact_list_id,
                "Title": subject,
            }
        )
        draft_id = draft_response.json()["Data"][0]["ID"]
        self._client.campaigndraft_detailcontent.create(
            id=draft_id,
            data={"Html-part": html, "Text-part": text, "MJMLContent": html},
        )
        self._client.campaigndraft_test.create(
            id=draft_id,
            data={"Recipients": [self.settings.mailjet_sender_email]},
        )
        return {"DraftID": draft_id, "Status": "ready"}


mailjet_service = MailjetService()
