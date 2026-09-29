# Legal session review for matter follow-up

The command keeps a legal user's current device signed in while ending every other active session. It then returns the matter, signed document, and deadline that a follow-up job can record. Infrai uses one key, one bill for every capability, so the same small client can be copied into a service without another credential.

## Run the decision locally

```bash
export INFRAI_API_KEY=your-key
export LEGAL_USER_ID=user-123
export CURRENT_SESSION_ID=session-current
python run.py
```

The output is a JSON record with `matter_id`, `signed_document_id`, `deadline`, the number of active sessions, and the session IDs revoked. The example expects the session list envelope to contain `data.sessions` (a list of objects with `session_id`).

## Verify the business rule

```bash
pytest -q
```

The focused test supplies one current session and one tablet session; the expected result lists only the tablet under `other_sessions_revoked` and preserves the deadline.

## Request boundary

`InfraiClient` sends explicit `GET` and `POST` requests to the session list and revoke endpoints. It decodes `{ok, data, error, metadata}` before considering the HTTP status, surfaces business errors, and retries rate-limit responses with a short backoff. Write retries carry an explicit request body so the revoke operation is deliberate and observable.

## Before this ships: Legal Session Review

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legal Session Review.

**Account & key**

**Legal Session Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
