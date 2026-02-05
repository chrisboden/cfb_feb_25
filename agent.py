import base64
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions,
    AssistantMessage, SystemMessage, ResultMessage,
    TextBlock, ToolUseBlock
)

app = FastAPI()

SETTINGS_AGENT_PATH = ".claude/settings_agent.json"
SETTINGS_AGENT_OPENROUTER_PATH = ".claude/settings_agent_openrouter.json"
# Normie toggle: set to True to use OpenRouter, False to use native Claude Code.
USE_OPENROUTER = True
ACTIVE_SETTINGS_PATH = (
    SETTINGS_AGENT_OPENROUTER_PATH if USE_OPENROUTER else SETTINGS_AGENT_PATH
)

current_client: ClaudeSDKClient | None = None
current_session_id: str | None = None


@app.get("/", response_class=HTMLResponse)
async def index():
    return Path("index.html").read_text()


@app.post("/reset")
async def reset():
    global current_client, current_session_id
    if current_client:
        await current_client.disconnect()
        current_client = None
    old_session = current_session_id
    current_session_id = None
    return {"status": "ok", "cleared_session": old_session}


@app.post("/interrupt")
async def interrupt():
    global current_client
    if current_client:
        await current_client.interrupt()
        return {"status": "ok", "interrupted": True}
    return {"status": "ok", "interrupted": False}


@app.post("/chat")
async def chat(request: Request):
    global current_client, current_session_id
    data = await request.json()
    prompt = data.get("message", "")

    async def generate():
        global current_client, current_session_id
        has_text_response = False

        options = ClaudeAgentOptions(
            system_prompt={"type": "preset", "preset": "claude_code"},
            settings=ACTIVE_SETTINGS_PATH,
            setting_sources=["project"],
        )
        if current_session_id:
            options.resume = current_session_id

        current_client = ClaudeSDKClient(options=options)
        await current_client.connect()
        await current_client.query(prompt)

        async for message in current_client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        if block.text.strip():
                            yield f"data: {json.dumps(block.text)}\n\n"
                            has_text_response = True
                    elif isinstance(block, ToolUseBlock):
                        try:
                            tool_input = json.dumps(block.input, ensure_ascii=False)
                        except Exception:
                            tool_input = str(block.input)
                        encoded_input = base64.b64encode(tool_input.encode("utf-8")).decode("ascii")
                        yield f"data: {json.dumps(f'[Using {block.name}|{encoded_input}]')}\n\n"

            elif isinstance(message, SystemMessage):
                if message.subtype in ('permission_request', 'permission_denied', 'tool_blocked'):
                    yield f"data: {json.dumps(f'[Permission: {message.subtype}]')}\n\n"
                elif message.subtype == 'init':
                    new_session_id = message.data.get('session_id')
                    if new_session_id and new_session_id != current_session_id:
                        current_session_id = new_session_id

            elif isinstance(message, ResultMessage):
                pass

        if not has_text_response:
            yield f"data: {json.dumps('[Agent completed without text response]')}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
