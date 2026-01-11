# 🐰 Grabbit — LLM Tool Reference

> **Purpose:** AI-native shopping list tracker for managing items to buy, with support for stores, categories, priorities, and gift tracking.
>
> **When to use:** User wants to track shopping items, check what to buy at a store, manage gift ideas, or mark items as purchased.

## Setup

```python
from src.tracker import grabbit
```

The `grabbit` instance is ready to use immediately.

---

## Core Commands

### 1. Add Item

Add something to the shopping list.

```python
grabbit.add(
    item: str,                    # Required: what to buy
    store: str = None,            # Optional: where to buy (Costco, Amazon, Target...)
    category: str = "other",      # groceries | household | clothing | electronics | gifts | other
    for_person: str = "self",     # "self" or person's name for gifts
    notes: str = None,            # Optional: extra details
    priority: str = "medium",     # low | medium | high | urgent
    url: str = None,              # Optional: link to item
    price: float = None,          # Optional: estimated cost
    recurring: bool = False,      # Is this a regular purchase?
    source: str = "manual"        # How it was added
) -> dict
```

**Returns:**
```python
{
    "success": True,
    "message": "🐰 Grabbed! Added 'oat milk' (Costco)",
    "item": { ... }  # Full item dict
}
```

**Examples:**
```python
# Simple add
grabbit.add("eggs")

# With store
grabbit.add("oat milk", store="Costco")

# Urgent item
grabbit.add("diapers", store="Costco", priority="urgent")

# Gift idea
grabbit.add("Kindle Paperwhite", for_person="Sowmya", category="gifts", 
            notes="She mentioned wanting to read more")

# Clothing with notes
grabbit.add("work pants", category="clothing", notes="Business casual, size 32")

# Online item with URL
grabbit.add("USB-C cable", store="Amazon", url="https://amazon.com/...")
```

---

### 2. List Items

Get items with optional filters.

```python
grabbit.list(
    status: str = "needed",       # needed | bought | archived | all
    store: str = None,            # Filter by store
    category: str = None,         # Filter by category
    for_person: str = None,       # Filter by recipient
    priority: str = None          # Filter by priority
) -> dict
```

**Returns:**
```python
{
    "count": 5,
    "items": [ ... ],  # List of item dicts, sorted by priority
    "filters": { ... }
}
```

**Examples:**
```python
grabbit.list()                           # All needed items
grabbit.list(status="all")               # Everything including bought
grabbit.list(store="Costco")             # Items for Costco
grabbit.list(category="groceries")       # Just groceries
grabbit.list(priority="urgent")          # Urgent items only
```

---

### 3. Shortcut Queries

Convenient methods for common queries.

```python
# What do I need at this store?
grabbit.at_store("Costco") -> dict

# What gift ideas do I have for this person?
grabbit.for_person("Sowmya") -> dict

# What's urgent?
grabbit.urgent() -> dict

# Search by name or notes
grabbit.search("milk") -> dict

# List all stores with item counts
grabbit.stores() -> dict
```

---

### 4. Mark as Bought

Mark an item as purchased.

```python
# By ID
grabbit.mark_bought(item_id="abc123") -> dict

# By name (searches for match)
grabbit.mark_bought(item_name="oat milk") -> dict
```

**Returns:**
```python
{
    "success": True,
    "message": "🐰 Nice grab! Marked 'oat milk' as bought.",
    "item": { ... }
}
```

**Note:** If searching by name finds multiple matches, returns them for clarification.

---

### 5. Archive / Delete

```python
# Archive (keeps history, removes from active list)
grabbit.archive(item_id: str) -> dict

# Delete permanently
grabbit.delete(item_id: str) -> dict
```

---

### 6. Update Item

Modify an existing item.

```python
grabbit.update(item_id: str, **updates) -> dict
```

**Examples:**
```python
grabbit.update("abc123", priority="urgent")
grabbit.update("abc123", store="Target", notes="Changed my mind")
```

---

### 7. Summary & Stats

```python
# Overall summary
grabbit.summary() -> {
    "total_needed": 10,
    "total_bought": 5,
    "urgent": 2,
    "by_category": {"groceries": 5, "household": 3, ...},
    "stores": {"Costco": 4, "Amazon": 2}
}

# Recent purchases
grabbit.recent_purchases(days=7) -> dict
```

---

## Conversational Patterns

Map user intents to Grabbit commands:

| User Intent | Command |
|-------------|---------|
| "Add X to my list" | `grabbit.add("X")` |
| "Add X to groceries" | `grabbit.add("X", category="groceries")` |
| "Need X from Costco" | `grabbit.add("X", store="Costco")` |
| "Add X, it's urgent" | `grabbit.add("X", priority="urgent")` |
| "Gift idea for Y: X" | `grabbit.add("X", for_person="Y", category="gifts")` |
| "What do I need?" | `grabbit.list()` |
| "What to get at Costco?" | `grabbit.at_store("Costco")` |
| "What should I get Y?" | `grabbit.for_person("Y")` |
| "What's urgent?" | `grabbit.urgent()` |
| "Got the X" / "Bought X" | `grabbit.mark_bought(item_name="X")` |
| "Remove X from list" | `grabbit.archive(item_id)` or `grabbit.delete(item_id)` |
| "Shopping list summary" | `grabbit.summary()` |

---

## Store Normalization

Common store names are normalized automatically:

| Input | Normalized |
|-------|------------|
| "amazon", "Amazon" | "Amazon" |
| "costco" | "Costco" |
| "tj", "trader joes" | "Trader Joe's" |
| "whole foods", "wholefoods" | "Whole Foods" |
| "home depot", "homedepot" | "Home Depot" |

---

## Category Aliases

| Input | Normalized |
|-------|------------|
| "grocery", "food" | "groceries" |
| "home", "house" | "household" |
| "clothes", "apparel" | "clothing" |
| "tech", "gadget" | "electronics" |
| "gift", "present" | "gifts" |

---

## Data Storage

- **Location:** `data/items.json`
- **Format:** JSON array of item objects
- **Persistence:** Immediate write on every change
- **No external dependencies**

---

## Error Handling

All methods return a dict with `success` boolean:

```python
# Success
{"success": True, "message": "...", "item": {...}}

# Failure
{"success": False, "message": "🐰 Couldn't find that item!"}
```

---

## Best Practices for LLM Agents

1. **Use `item_name` for mark_bought** — More natural than requiring IDs
2. **Include store when known** — Better organization
3. **Use `for_person` for gifts** — Enables gift idea queries later
4. **Set priority for urgent items** — Helps user prioritize
5. **Add notes for specifics** — "Size M", "Organic", "The blue one"
6. **Use categories** — Enables filtering and organization
