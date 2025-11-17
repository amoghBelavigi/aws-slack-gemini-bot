import json, time, hmac, hashlib, os
import requests
from langgraph_rag import run_rag

SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"].encode()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

def verify_slack(headers, body):
    ts = headers.get("X-Slack-Request-Timestamp")
    sig = headers.get("X-Slack-Signature")

    if abs(time.time() - int(ts)) > 300:
        return False

    base = f"v0:{ts}:{body.decode()}"
    digest = hmac.new(SLACK_SIGNING_SECRET, base.encode(), hashlib.sha256).hexdigest()
    expected = f"v0={digest}"

    return hmac.compare_digest(expected, sig)

async def handle_slack_event(headers, body):
    if not verify_slack(headers, body):
        return {"statusCode": 403, "body": "invalid signature"}

    payload = json.loads(body)

    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    event = payload.get("event", {})
    if event.get("subtype") == "bot_message":
        return {"statusCode": 200, "body": "ignored"}

    question = event.get("text", "").strip()
    channel = event.get("channel")
    thread = event.get("thread_ts") or event.get("ts")

    answer = run_rag(question)

    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
        data={
            "channel": channel,
            "thread_ts": thread,
            "text": answer
        },
    )

    return {"statusCode": 200, "body": "ok"}
