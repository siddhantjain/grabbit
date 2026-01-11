# 🐰 Grabbit

**An AI-native shopping list tracker with personality.**

Grabbit is a friendly rabbit that keeps track of everything you need to buy. Built for LLM agents, it provides a simple Python interface for managing shopping lists with support for stores, categories, priorities, and gift tracking.

## Features

- 🛒 **Smart Shopping Lists** — Track items to buy with status (needed/bought/archived)
- 🏪 **Store Organization** — Associate items with stores (Costco, Amazon, Target, etc.)
- 🎁 **Gift Tracking** — Save gift ideas for people ("Sowmya wants a Kindle")
- 🚨 **Priority Levels** — Mark items as urgent, high, medium, or low priority
- 📂 **Categories** — Organize by type: groceries, household, clothing, electronics, gifts
- 🌐 **Web Dashboard** — Mobile-friendly UI with secret URL authentication
- 🤖 **AI-Native Design** — Built specifically for LLM agents to use as a tool

## Installation

```bash
git clone https://github.com/siddhantjain/grabbit.git
cd grabbit
```

No dependencies required beyond Python 3.8+.

## Quick Start

```python
from src.tracker import grabbit

# Add items
grabbit.add("oat milk", store="Costco", category="groceries")
grabbit.add("diapers", store="Costco", priority="urgent")
grabbit.add("Kindle", for_person="Sowmya", category="gifts", notes="She wants to read more")

# Query items
grabbit.list()                      # All needed items
grabbit.at_store("Costco")          # What to get at Costco
grabbit.for_person("Sowmya")        # Gift ideas for Sowmya
grabbit.urgent()                    # Urgent items only

# Mark as bought
grabbit.mark_bought(item_name="oat milk")

# Get summary
grabbit.summary()
```

## LLM Tool Reference

Grabbit is designed for use as an LLM tool. See [TOOL.md](TOOL.md) for the complete API reference with examples.

### Common Conversational Patterns

| User Says | LLM Action |
|-----------|------------|
| "Add milk to my shopping list" | `grabbit.add("milk", category="groceries")` |
| "Need diapers from Costco, urgent" | `grabbit.add("diapers", store="Costco", priority="urgent")` |
| "What do I need at Costco?" | `grabbit.at_store("Costco")` |
| "What should I get for Sowmya?" | `grabbit.for_person("Sowmya")` |
| "Got the milk" | `grabbit.mark_bought(item_name="milk")` |
| "What's urgent?" | `grabbit.urgent()` |
| "Show my shopping list" | `grabbit.list()` |

## Web Dashboard

Grabbit includes a web dashboard for viewing and managing items.

### Start the Server

```bash
python -m src.server
```

The server runs on port 4005 by default with secret URL authentication.

### Features

- 📱 Mobile-friendly responsive design
- 🔍 Filter by store
- ✅ Quick mark-as-bought buttons
- 📦 Archive items
- ➕ Add items directly from the UI

## Data Model

```python
{
    "id": "abc123",           # Auto-generated short ID
    "item": "oat milk",       # Item name
    "status": "needed",       # needed | bought | archived
    "store": "Costco",        # Optional: where to buy
    "category": "groceries",  # groceries | household | clothing | electronics | gifts | other
    "for_person": "self",     # self | person's name (for gifts)
    "notes": "Organic",       # Optional: extra details
    "priority": "medium",     # low | medium | high | urgent
    "url": null,              # Optional: link to item online
    "price": null,            # Optional: estimated cost
    "added_at": "ISO8601",    # When added
    "bought_at": null,        # When purchased (if bought)
    "recurring": false,       # Regular purchase?
    "source": "manual"        # manual | voice | api
}
```

## Data Storage

All data is stored locally in JSON files:

```
data/
├── items.json          # Shopping list items
└── .dashboard_secret   # Secret for dashboard URL auth
```

No cloud sync. No external dependencies. Your data stays local.

## API Endpoints

The dashboard server also exposes a JSON API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/list` | GET | List items (supports `?status=`, `?store=`, `?category=`) |
| `/api/summary` | GET | Get shopping list summary |
| `/api/stores` | GET | List all stores with item counts |
| `/api/add` | POST | Add a new item |
| `/api/mark_bought` | POST | Mark item as bought |
| `/api/archive` | POST | Archive an item |

All endpoints require the secret path prefix (e.g., `/{secret}/api/list`).

## Why "Grabbit"?

Because it's a **grab** list managed by a rab**bit**! 🐰

The rabbit personality adds some fun:
- "🐰 Grabbed! Added 'oat milk'"
- "🐰 Nice grab! Marked 'milk' as bought"
- "🐰 Nothing to grab! Your list is empty."

## License

MIT — use it however you like!

## Author

Built by [Neo](https://github.com/siddhantjain) 🐙 (Siddhant's AI assistant)
