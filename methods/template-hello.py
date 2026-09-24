import json

import zapqio

from lib.greetings import greeting


def run(data: str) -> str:
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("Input must be valid JSON.") from None

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("The 'name' field must be a non-empty string.")

    check_secret = payload.get("check_secret", False)
    if not isinstance(check_secret, bool):
        raise ValueError("The 'check_secret' field must be a boolean.")

    if check_secret:
        token = zapqio.constants.get("EXAMPLE_API_TOKEN")
        if not token:
            raise ValueError("The EXAMPLE_API_TOKEN constant is empty.")

    zapqio.log.info("Example method completed.")

    return json.dumps(
        {
            "message": greeting(name.strip()),
            "secret_loaded": check_secret,
        },
        ensure_ascii=False,
    )
