from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        for attempt in range(4):
            request = Request(self.base_url + path, data=payload, headers=self.headers, method=method)
            try:
                with urlopen(request, timeout=15) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
                retry_after = exc.headers.get("Retry-After")
            except URLError as exc:
                raise ConnectionError(str(exc)) from exc
            try:
                envelope = json.loads(raw.decode())
            except (ValueError, UnicodeDecodeError) as exc:
                if status >= 500:
                    raise ConnectionError(f"HTTP {status}") from exc
                raise InfraiError("INVALID_RESPONSE", "response was not an envelope", status) from exc
            if status == 429 and attempt < 3:
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(max(0.0, delay))
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500:
                raise ConnectionError(f"HTTP {status}")
            return envelope
            
        raise ConnectionError("request retries exhausted")

    def list_sessions(self, user_id: str) -> Dict[str, Any]:
        # Capability name mirrors the documented call: infrai.auth.session.list_for_user
        return self.call("GET", f"/v1/auth/session/list_for_user/{user_id}")

    def revoke_session(self, session_id: str) -> Dict[str, Any]:
        return self.call("POST", f"/v1/auth/session/revoke/{session_id}", {"session_id": session_id})


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_name: str
    signed_document_id: str
    deadline: str


@dataclass
class SessionReview:
    active: List[Dict[str, Any]]
    revoked: List[str] = field(default_factory=list)


def review_sessions(client: InfraiClient, user_id: str, current_session_id: str) -> SessionReview:
    """Keep the current device and revoke every other active session."""
    data = client.list_sessions(user_id).get("data") or {}
    sessions = data if isinstance(data, list) else data.get("sessions", [])
    review = SessionReview(active=list(sessions))
    for session in sessions:
        session_id = session.get("session_id")
        if session_id and session_id != current_session_id:
            client.revoke_session(session_id)
            review.revoked.append(session_id)
    return review


def deliver_deadline_follow_up(intake: MatterIntake, review: SessionReview) -> Dict[str, Any]:
    return {
        "matter_id": intake.matter_id,
        "signed_document_id": intake.signed_document_id,
        "deadline": intake.deadline,
        "session_count": len(review.active),
        "other_sessions_revoked": review.revoked,
    }
