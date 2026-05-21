import json
import os
from datetime import datetime


def log_prompt(
    agent_name,
    prompt,
    response
):

    log_entry = {
        "timestamp": str(datetime.now()),
        "agent": agent_name,
        "prompt": prompt,
        "response": response
    }

    os.makedirs("logs", exist_ok=True)

    with open(
        "logs/prompt_logs.jsonl",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(log_entry)
            + "\n"
        )
