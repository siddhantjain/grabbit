# Grabbit 🐰 — LLM Tool Reference

> Your friendly shopping list rabbit! Track things to buy, where to get them, and who they're for.

## Setup

```python
from src.tracker import grabbit
```

---

## Commands

### 1. Add Item

Add something to grab.

```python
grabbit.add(item, store=None, category="other", for_person="self", 
            notes=None, priority="medium", url=None, price=None, 
            recurring=False, source="manual")
```

**Parameters:**
- `item` (str): What to buy — "oat milk", "birthday gift for Sowmya"
- `store` (str): Where to buy — "Costco", "Amazon", "Target"
- `category` (str): Type — groceries|household|clothing|electronics|gifts|other
- `for_person` (str): Who it's for — "self" or name like "Sowmya"
- `notes` (str): Extra details — "the organic kind", "size medium"
- `priority` (str): Urgency — low|medium|high|urgent
- `url` (str): Link to item online
- `price` (float): Estimated cost
- `recurring` (bool): Regular purchase?
- `source` (str): Origin — manual|google_keep|whatsapp

**Examples:**
```python
grabbit.add("oat milk")
grabbit.add("diapers", store="Costco", priority="urgent")
grabbit.add("Kindle", for_person="Sowmya", category="gifts", notes="She mentioned wanting one")
grabbit.add("work pants", category="clothing", notes="Business casual")
```

---

### 2. List Items

Get items with optional filters.

```python
grabbit.list(status="needed", store=None, category=None, for_person=None, priority=None)
```

**Status options:** needed | bought | archived | all

**Shortcuts:**
```python
grabbit.at_store("Costco")      # What to grab at Costco
grabbit.for_person("Sowmya")    # Gift ideas for Sowmya
grabbit.urgent()                 # Urgent items only
```

---

### 3. Mark Bought

```python
grabbit.mark_bought(item_id="abc123")
# or
grabbit.mark_bought(item_name="oat milk")  # Searches by name
```

---

### 4. Archive / Delete

```python
grabbit.archive("abc123")  # Remove from list but keep history
grabbit.delete("abc123")   # Permanently delete
```

---

### 5. Update Item

```python
grabbit.update("abc123", store="Target", priority="high")
```

---

### 6. Search

```python
grabbit.search("milk")  # Search by name or notes
```

---

### 7. Get Info

```python
grabbit.summary()              # Overview stats
grabbit.stores()               # List stores with item counts
grabbit.recent_purchases(7)    # What was bought in last 7 days
```

---

## Data Storage

- Items: `data/items.json`
- Dashboard secret: `data/.dashboard_secret`

---

## Dashboard

Access at: `https://jain-ai.exe.xyz:4002/{secret}/`

The secret URL path acts as authentication — bookmark it but don't share!

---

## Conversational Examples

| User says | What to do |
|-----------|------------|
| "Add milk to my shopping list" | `grabbit.add("milk", category="groceries")` |
| "Need diapers from Costco, urgent" | `grabbit.add("diapers", store="Costco", priority="urgent")` |
| "Add a gift idea for Sowmya - Kindle" | `grabbit.add("Kindle", for_person="Sowmya", category="gifts")` |
| "What do I need at Costco?" | `grabbit.at_store("Costco")` |
| "What should I get Sowmya?" | `grabbit.for_person("Sowmya")` |
| "Got the milk" | `grabbit.mark_bought(item_name="milk")` |
| "What's urgent?" | `grabbit.urgent()` |
| "Show my shopping list" | `grabbit.list()` |
