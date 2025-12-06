import json
from datetime import datetime

LOG_FILE = "logs/company_matching_elk.jsonl"

def elk_log(event, input=None, matched=None, score=None, reason=None, level="INFO"):
    doc = {
        "@timestamp": datetime.utcnow().isoformat(),
        "event": event,
        "input": input,
        "matched": matched,
        "score": score,
        "reason": reason,
        "level": level,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(doc) + "\n")
