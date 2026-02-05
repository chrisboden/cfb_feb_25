# Claude Agent SDK Starter

Minimal starter for building agents with the Claude Agent SDK.

## Quickstart

1. Install deps: `python -m pip install -r requirements.txt`
2. Run the server: `python agent.py`
3. Open `index.html` in your browser
4. Chat with your agent

That's it. The agent will follow whatever instructions you put in `CLAUDE.md`.

### What the Agent Can Do (Out of the Box)

By default, the agent has full coding capabilities:
- **Read & search files** - navigate and understand any codebase
- **Edit & write files** - make changes, create new files
- **Run shell commands** - execute builds, tests, git operations
- **Search the web** - fetch documentation, look up APIs
- **Ask clarifying questions** - interactive back-and-forth

### Adding Skills

Drop skill folders into `.claude/skills/` to give your agent specialist knowledge. Skills are markdown docs the agent can reference for specific tasks (e.g., SDK documentation, coding standards, domain knowledge).

## For Coding Agents

This codebase is a minimal reference implementation. Your job is to extend it.

### Key Files

- `agent.py` - FastAPI server wrapping the Claude Agent SDK
- `index.html` - Basic chat UI for testing
- `.claude/settings_agent.json` - **All configuration lives here** (permissions, allowed tools, env vars, API routing).
- `.claude/CLAUDE.md` - Project context injected into agent system prompt

### Configuration via settings_agent.json

Do not hardcode permissions or tool lists in `agent.py`. All config is managed in `.claude/settings_agent.json`:

- `permissions.default` - Permission mode (`acceptEdits`, `default`, `bypassPermissions`)
- `permissions.allow` - Explicitly allowed tools
- `permissions.deny` - Blocked paths/operations
- `env` - Environment variables for API routing (optional)

### Using OpenRouter Instead of Claude Code Account

By default, the agent uses your Claude Code account. To use models via OpenRouter instead:

1. Open `agent.py`
2. Set `USE_OPENROUTER = True`
3. Make sure `.claude/settings_agent_openrouter.json` has your OpenRouter API key and models

You can swap in any OpenRouter-supported models for haiku/sonnet/opus tiers in `.claude/settings_agent_openrouter.json`.

### Useful Skills

Use these to understand the SDK and CLI:

- `/cc-agent-sdk` - Claude Agent SDK documentation (Python/TypeScript API, permissions, sessions, MCP, hooks)
- `/cc-know-thyself` - Claude Code CLI documentation (tools, settings, slash commands)

### Architecture

```
User → index.html → FastAPI /chat → claude_agent_sdk.query() → Claude (or OpenRouter)
                                            ↓
                              .claude/settings_agent*.json (permissions, tools, API routing)
                              .claude/CLAUDE.md (project context)
```

### Session Continuity

Conversations maintain context via `session_id`:
- First message creates a new session, ID is stored
- Subsequent messages pass `resume=session_id` to continue the conversation
- Agent remembers what was said earlier in the thread
- Reset button (`/reset` endpoint) clears session for fresh start

### Current State

Minimal working chat harness with:
- Session continuity (multi-turn conversations)
- Debug logging to terminal
- Tool usage visibility in chat
- Permission issue surfacing

Ready for extension.
