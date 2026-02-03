import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from claude_agent_sdk import (
    query, ClaudeAgentOptions,
    AssistantMessage, SystemMessage, ResultMessage, UserMessage,
    TextBlock, ToolUseBlock, ToolResultBlock, ThinkingBlock
)

app = FastAPI()

# Store session ID for conversation continuity
current_session_id = None


@app.get("/", response_class=HTMLResponse)
async def index():
    return Path("index.html").read_text()


@app.post("/reset")
async def reset():
    global current_session_id
    old_session = current_session_id
    current_session_id = None
    print(f"\n[SESSION RESET] Cleared session: {old_session}")
    return {"status": "ok", "cleared_session": old_session}


@app.post("/chat")
async def chat(request: Request):
    global current_session_id
    data = await request.json()
    prompt = data.get("message", "")

    print(f"\n{'='*60}")
    print(f"USER PROMPT: {prompt}")
    print(f"{'='*60}")

    async def generate():
        global current_session_id
        has_text_response = False

        # Build options - resume session if we have one
        options = ClaudeAgentOptions(
            system_prompt={"type": "preset", "preset": "claude_code"},
            setting_sources=["project"],  # Load from .claude/settings.json
        )
        if current_session_id:
            options.resume = current_session_id
            print(f"  Resuming session: {current_session_id}")

        async for message in query(prompt=prompt, options=options):
            # Debug: print all messages to terminal
            if isinstance(message, AssistantMessage):
                print(f"\n[ASSISTANT MESSAGE]")
                for block in message.content:
                    if isinstance(block, TextBlock):
                        if block.text.strip():
                            print(f"  TEXT: {block.text[:200]}{'...' if len(block.text) > 200 else ''}")
                            yield f"data: {json.dumps(block.text)}\n\n"
                            has_text_response = True
                        else:
                            print(f"  TEXT: (empty)")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  TOOL USE: {block.name}")
                        print(f"    Input: {block.input}")
                        # Show tool usage in chat
                        yield f"data: {json.dumps(f'[Using {block.name}...]')}\n\n"
                    elif isinstance(block, ToolResultBlock):
                        content_preview = str(block.content)[:200] if block.content else "None"
                        print(f"  TOOL RESULT: {content_preview}...")
                    elif isinstance(block, ThinkingBlock):
                        print(f"  THINKING: {block.thinking[:100]}...")
                    else:
                        print(f"  UNKNOWN BLOCK: {type(block).__name__}")

            elif isinstance(message, SystemMessage):
                print(f"\n[SYSTEM MESSAGE] subtype={message.subtype}")
                # Highlight permission-related messages
                if message.subtype in ('permission_request', 'permission_denied', 'tool_blocked'):
                    print(f"  ⚠️  PERMISSION ISSUE: {message.subtype}")
                    print(f"  Data: {json.dumps(message.data, indent=2)}")
                    yield f"data: {json.dumps(f'[⚠️ Permission: {message.subtype}]')}\n\n"
                elif message.subtype == 'init':
                    # Capture session ID for continuity
                    new_session_id = message.data.get('session_id')
                    if new_session_id and new_session_id != current_session_id:
                        current_session_id = new_session_id
                        print(f"  Session: {current_session_id} (stored)")
                    else:
                        print(f"  Session: {current_session_id} (continued)")
                    print(f"  Model: {message.data.get('model', 'unknown')}")
                    print(f"  Tools: {len(message.data.get('tools', []))} tools")
                    print(f"  Skills: {message.data.get('skills', [])}")
                else:
                    print(f"  Data: {message.data}")

            elif isinstance(message, ResultMessage):
                print(f"\n[RESULT MESSAGE] subtype={message.subtype}")
                print(f"  is_error: {message.is_error}")
                print(f"  num_turns: {message.num_turns}")
                print(f"  duration_ms: {message.duration_ms}")
                if message.result:
                    print(f"  result: {message.result[:200]}...")

            elif isinstance(message, UserMessage):
                print(f"\n[USER MESSAGE]")
                print(f"  Content: {message.content}")

            else:
                print(f"\n[UNKNOWN MESSAGE TYPE] {type(message).__name__}")
                print(f"  {message}")

        if not has_text_response:
            print("  WARNING: No text response generated!")
            yield f"data: {json.dumps('[Agent completed without text response - check terminal for details]')}\n\n"

        print(f"\n{'='*60}")
        print("STREAM COMPLETE")
        print(f"{'='*60}\n")
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
