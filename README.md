# Claude Agent SDK Starter

Boilerplate for building agents with the Claude Agent SDK.

## For Coding Agents

This codebase is a minimal reference implementation. Your job is to extend it.

### Key Files

- `agent.py` - FastAPI server wrapping the Claude Agent SDK
- `index.html` - Basic chat UI for testing
- `.claude/settings.json` - **All configuration lives here** (permissions, allowed tools, env vars, API routing)
- `.claude/CLAUDE.md` - Project context injected into agent system prompt

### Configuration via settings.json

Do not hardcode permissions or tool lists in `agent.py`. All config is managed in `.claude/settings.json`:

- `permissions.default` - Permission mode (`acceptEdits`, `default`, `bypassPermissions`)
- `permissions.allow` - Explicitly allowed tools
- `permissions.deny` - Blocked paths/operations
- `env` - Environment variables including API routing (currently OpenRouter)

### Available Skills

Use these to understand the SDK and CLI:

- `/cc-agent-sdk` - Claude Agent SDK documentation (Python/TypeScript API, permissions, sessions, MCP, hooks)
- `/cc-docs` or `/cc-know-thyself` - Claude Code CLI documentation (tools, settings, slash commands)

### Architecture

```
User → index.html → FastAPI /chat → claude_agent_sdk.query() → Claude via OpenRouter
                                            ↓
                              .claude/settings.json (permissions, tools)
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
