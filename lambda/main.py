from fastapi import FastAPI, Request
from mangum import Mangum
from slack_handler import handle_slack_event

app = FastAPI()

@app.post("/slack/events")
async def slack_events(request: Request):
    body = await request.body()
    headers = request.headers
    return await handle_slack_event(headers, body)

lambda_handler = Mangum(app)
