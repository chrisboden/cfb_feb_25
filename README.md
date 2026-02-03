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
- `env` - Environment variables for API routing (optional)

### Using OpenRouter Instead of Claude Code Account

By default, the agent uses your Claude Code account. To use models via OpenRouter instead:

1. Copy the contents of `.claude/settings_openrouter.json` into `.claude/settings.json`
2. Replace `sk-or-v1-...` with your actual OpenRouter API key

The OpenRouter config routes requests through OpenRouter's API and lets you specify which models to use:

```json
"env": {
  "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
  "ANTHROPIC_AUTH_TOKEN": "sk-or-v1-your-key-here",
  "ANTHROPIC_API_KEY": "",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL": "x-ai/grok-4.1-fast",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "moonshotai/kimi-k2.5",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "openai/gpt-5.2-codex"
}
```

You can swap in any OpenRouter-supported models for haiku/sonnet/opus tiers.

### Useful Skills

Use these to understand the SDK and CLI:

- `/cc-agent-sdk` - Claude Agent SDK documentation (Python/TypeScript API, permissions, sessions, MCP, hooks)
- `/cc-know-thyself` - Claude Code CLI documentation (tools, settings, slash commands)

### Architecture

```
User → index.html → FastAPI /chat → claude_agent_sdk.query() → Claude (or OpenRouter)
                                            ↓
                              .claude/settings.json (permissions, tools, API routing)
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
