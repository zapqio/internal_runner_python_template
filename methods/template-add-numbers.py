import json
import math

import zapqio


def run(data: str) -> str:
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("Input must be valid JSON.") from None

    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")

    for field in ("a", "b"):
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"The '{field}' field must be a finite number.")

        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"The '{field}' field must be a finite number.")

    total = payload["a"] + payload["b"]
    if isinstance(total, float) and not math.isfinite(total):
        raise ValueError("The sum must be a finite number.")

    result = json.dumps({"sum": total}, allow_nan=False)
    zapqio.log.info("Numbers added.")
    return result
