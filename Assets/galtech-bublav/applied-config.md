# Galtech BubblaV chatbot — applied configuration

Live chatbot on **galtechtrading.com** via BubblaV (website id `95d7115b-7d11-4239-a7a9-e34e1d28e01d`, Pro plan). Configured 2026-06-28/29 through the BubblaV MCP.

## How to manage it (for future edits)
- Endpoint: `POST https://www.bubblav.com/api/mcp` (JSON-RPC 2.0; method `tools/call`, params `{name, arguments}`).
- Auth: header `X-API-Key: bubblav_mcp_…` (the MCP key from Dashboard → Settings → API keys; **secret — not stored here**).
- Or add it in Claude → Settings → Connectors as an MCP server (`https://www.bubblav.com/api/mcp`, OAuth).
- 43 tools available (read + write): website settings, widget, knowledge, forms, handoff, custom tools, crawl, analytics/insights. Docs: https://docs.bubblav.com/developer-guide/mcp-server.md
- Helper used: `/tmp/bubcall.py` (`call(tool, args)` over JSON-RPC).

## What was configured

**System prompt** (`update_website_settings.custom_instructions`, ≤2000 chars): Galtech Agent persona — B2B distributor voice, answer-then-next-step, surface/link products, **never quote prices/stock/lead times**, capture leads, prioritise *Become a Dealer*, no fabrication, EN/AR, scope + contacts. (Was previously empty.)

**Forms** (5 total):
- **Become a Dealer** — *new*, the priority conversion. Fields: company, contact, business type, work email, phone/WhatsApp, country & city, brands of interest, website, message. Triggers on dealer/reseller/trade-account/partnership/distribution intent.
- **Quote Request** — retargeted for B2B: products/brands of interest, quantity (units/zones), project type, timeline, notes (removed the consumer "budget range"). Triggers on price/quote/proposal/BOM.
- **Lead Capture** — retargeted as the general callback (when it's not a quote or dealer request).
- **Support Request**, **Newsletter** — left as-is (escalation / updates).

**Human-handoff scenarios** (3): explicit "talk to a human/sales rep"; urgent issue / complaint / warranty-RMA; existing dealer asking about order/invoice/account.

**Knowledge entries** (6 added, indexed & searchable): Becoming a Galtech Dealer · Brands Galtech Distributes · Galtech Locations & Contact · Pricing & Availability Policy · Product Categories & Solutions · Training & Events.

**Widget**: quick-suggestions changed to *"How do I become a dealer?", "Which brands do you carry?", "Help me find products for a project", "Request a quote"*; intro line refreshed. (Bot name "Galtech Agent" kept.)

**Crawl**: 656 pages already indexed (products, brands, solutions, dealers) — powers product answers and links. Not changed.

## Notes / next options
- **Product cards**: BubblaV surfaces products from the crawled `/products/<slug>` pages (image + link). For richer, structured product cards you'd add an e-commerce integration or a `bubblav_create_custom_tool` pointing at a product-search endpoint (Galtech is a Framer site with no public product API today).
- Review **content gaps** periodically: `bubblav_get_content_gaps` / `bubblav_list_unanswered_questions`, then `bubblav_add_knowledge` to fill them.
- Full training rationale & copy: see [galtech-assistant-training.md](galtech-assistant-training.md).
