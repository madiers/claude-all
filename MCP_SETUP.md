# MCP setup — Galtech marketing

Persistent MCP config for this project. `.mcp.json` (repo root) is **committed to git**, so these servers travel with the repo and are never lost. When you open Claude Code in this folder it will prompt once to approve the project MCP servers — approve them.

## In `.mcp.json` (committed, no secrets)

| Server | URL | Auth | What it gives you |
|--------|-----|------|-------------------|
| **higgsfield** | `https://mcp.higgsfield.ai/mcp` | OAuth (browser, first use) | AI **image + video** generation — 30+ models (Seedance, Kling, Veo, Flux, Seedream, **gpt-image-class** models, etc.). Covers "GPT images for refs" **and** "different video models". |
| **context7** | `https://mcp.context7.com/mcp` | Keyless (free) | Up-to-date library/API docs on demand — saves tokens vs. web-scraping docs. |
| **bublav** | `https://www.bubblav.com/api/mcp` | `X-API-Key` via **env var** | Manage the Galtech website chatbot (BubblaV). |

### Secret for Bublav (never commit the key)
The key stays out of git — it's read from an env var. Set it once in your shell profile:
```bash
export BUBLAV_MCP_KEY="bublav_mcp_…"   # the key from BubblaV dashboard → Settings → API keys
```
`.mcp.json` references it as `${BUBLAV_MCP_KEY}`.

## Add via CLI (alternative / other machines)
```bash
# project scope = writes to this repo's .mcp.json (shareable, durable)
claude mcp add --scope project --transport http higgsfield https://mcp.higgsfield.ai/mcp
claude mcp add --scope project --transport http context7   https://mcp.context7.com/mcp
claude mcp add --scope project --transport http bublav      https://www.bubblav.com/api/mcp --header "X-API-Key: ${BUBLAV_MCP_KEY}"
# then:
claude mcp list
```
Use `--scope user` instead of `--scope project` to make a server available in every project (stored in your user config, not this repo).

## claude.ai connectors (account-level — manage in claude.ai, not here)
These were used earlier as **claude.ai Connectors** (OAuth, tied to your Claude account, not the repo): **Figma, Gmail, Google Calendar, Google Drive, Mailchimp, Supabase, Railway, Kiwi.com**. They persist on your account — if one shows as disconnected in a session, re-enable it at **claude.ai → Settings → Connectors**. They don't need to live in `.mcp.json`.

## Notes
- This session could not call Higgsfield/Context7 because they weren't attached to *this* run — once `.mcp.json` is approved (or the connectors re-enabled), they're available.
- Never hardcode API keys in `.mcp.json`; always use `${ENV_VAR}` (supported by Claude Code).
