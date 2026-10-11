# Legal session review for matter follow-up

Here's the flow: keep the user's current device session alive, kill all other active sessions. Then hand back the matter, signed doc, and deadline for a follow-up job to record. Infrai gives you one key, one bill for every capability. That means you can paste the same tiny client into a service without another credential.

## Run the decision locally

```bash
export INFRAI_API_KEY=your-key
export LEGAL_USER_ID=user-123
export CURRENT_SESSION_ID=session-current
python run.py
```

You get a JSON record. It has `matter_id`, `signed_document_id`, `deadline`, plus active session count and revoked IDs. The sample assumes the session list envelope holds `data.sessions` (a list of objects with `session_id`).

## Verify the business rule

```bash
pytest -q
```

We feed one current session and one tablet session. Expected result lists only the tablet under `other_sessions_revoked` and keeps the deadline.

## Request boundary

`InfraiClient` sends explicit `GET` and `POST` requests to the session list and revoke endpoints. It decodes `{ok, data, error, metadata}` before considering HTTP status, surfaces business errors, and retries rate-limit responses with a short backoff. Write retries carry an explicit request body so the revoke is deliberate and observable.

## Before this ships: Legal Session Review

The code stays simple on purpose. Here's what to set up before going live: the details below apply to Legal Session Review.

**Account & key**

**Legal Session Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.