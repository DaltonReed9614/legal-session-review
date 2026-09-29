from src.legal_sessions import InfraiClient, MatterIntake, SessionReview, deliver_deadline_follow_up


def test_revoke_sends_required_session_id():
    client = object.__new__(InfraiClient)
    calls = []
    client.call = lambda method, path, body: calls.append((method, path, body)) or {"ok": True}

    client.revoke_session("tablet")

    assert calls == [("POST", "/v1/auth/session/revoke/tablet", {"session_id": "tablet"})]


def test_deadline_follow_up_reports_revoked_devices():
    intake = MatterIntake("m-1", "Client", "doc-9", "2026-10-15")
    review = SessionReview([{"session_id": "current"}, {"session_id": "tablet"}], ["tablet"])
    result = deliver_deadline_follow_up(intake, review)
    assert result["other_sessions_revoked"] == ["tablet"]
    assert result["deadline"] == "2026-10-15"
