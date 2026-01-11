"""JSON file-based storage for Grabbit shopping tracker."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, asdict, field


@dataclass
class GrabbitItem:
    """A shopping list item."""
    id: str
    item: str
    status: str = "needed"  # needed | bought | archived
    store: Optional[str] = None
    category: str = "other"  # groceries | household | clothing | electronics | gifts | other
    for_person: str = "self"  # self | name of person (for gifts)
    notes: Optional[str] = None
    priority: str = "medium"  # low | medium | high | urgent
    url: Optional[str] = None
    price: Optional[float] = None
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    bought_at: Optional[str] = None
    recurring: bool = False
    source: str = "manual"  # manual | google_keep | whatsapp

    @classmethod
    def create(cls, item: str, **kwargs) -> "GrabbitItem":
        """Create a new item with auto-generated ID."""
        return cls(id=str(uuid.uuid4())[:8], item=item, **kwargs)


class GrabbitStore:
    """JSON file-based storage for shopping items."""

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.items_file = self.data_dir / "items.json"

    def _load(self) -> List[dict]:
        """Load all items from storage."""
        if self.items_file.exists():
            with open(self.items_file) as f:
                return json.load(f)
        return []

    def _save(self, items: List[dict]):
        """Save all items to storage."""
        with open(self.items_file, "w") as f:
            json.dump(items, f, indent=2)

    def add(self, item: GrabbitItem) -> dict:
        """Add a new item to the list."""
        items = self._load()
        item_dict = asdict(item)
        items.append(item_dict)
        self._save(items)
        return item_dict

    def get(self, item_id: str) -> Optional[dict]:
        """Get an item by ID."""
        items = self._load()
        for item in items:
            if item["id"] == item_id:
                return item
        return None

    def update(self, item_id: str, **updates) -> Optional[dict]:
        """Update an item by ID."""
        items = self._load()
        for i, item in enumerate(items):
            if item["id"] == item_id:
                items[i].update(updates)
                self._save(items)
                return items[i]
        return None

    def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        items = self._load()
        original_len = len(items)
        items = [item for item in items if item["id"] != item_id]
        if len(items) < original_len:
            self._save(items)
            return True
        return False

    def list_all(self, 
                 status: Optional[str] = None,
                 store: Optional[str] = None,
                 category: Optional[str] = None,
                 for_person: Optional[str] = None,
                 priority: Optional[str] = None) -> List[dict]:
        """List items with optional filters."""
        items = self._load()
        
        if status:
            items = [i for i in items if i.get("status") == status]
        if store:
            items = [i for i in items if (i.get("store") or "").lower() == store.lower()]
        if category:
            items = [i for i in items if i.get("category") == category]
        if for_person:
            items = [i for i in items if (i.get("for_person") or "").lower() == for_person.lower()]
        if priority:
            items = [i for i in items if i.get("priority") == priority]
        
        return items

    def search(self, query: str) -> List[dict]:
        """Search items by name or notes."""
        items = self._load()
        query_lower = query.lower()
        return [
            i for i in items 
            if query_lower in i.get("item", "").lower() 
            or query_lower in (i.get("notes") or "").lower()
        ]

    def mark_bought(self, item_id: str) -> Optional[dict]:
        """Mark an item as bought."""
        return self.update(
            item_id, 
            status="bought", 
            bought_at=datetime.utcnow().isoformat()
        )

    def archive(self, item_id: str) -> Optional[dict]:
        """Archive an item."""
        return self.update(item_id, status="archived")

    def get_stores(self) -> List[str]:
        """Get list of all unique stores."""
        items = self._load()
        stores = set()
        for item in items:
            if item.get("store"):
                stores.add(item["store"])
        return sorted(stores)

    def get_recent_purchases(self, days: int = 7) -> List[dict]:
        """Get items bought in the last N days."""
        items = self._load()
        cutoff = datetime.utcnow().timestamp() - (days * 86400)
        recent = []
        for item in items:
            if item.get("status") == "bought" and item.get("bought_at"):
                try:
                    bought_ts = datetime.fromisoformat(item["bought_at"]).timestamp()
                    if bought_ts >= cutoff:
                        recent.append(item)
                except:
                    pass
        return recent


# Default store instance
default_store = GrabbitStore()
