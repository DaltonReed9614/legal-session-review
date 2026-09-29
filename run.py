import json
import os

from src.legal_sessions import InfraiClient, MatterIntake, deliver_deadline_follow_up, review_sessions


def main() -> None:
    user_id = os.environ["LEGAL_USER_ID"]
    current = os.environ["CURRENT_SESSION_ID"]
    intake = MatterIntake("matter-1042", "Acme Holdings", "signed-778", "2026-10-15")
    result = deliver_deadline_follow_up(intake, review_sessions(InfraiClient(), user_id, current))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

