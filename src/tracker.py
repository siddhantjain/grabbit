"""Grabbit - AI-native shopping list tracker 🐰

A friendly rabbit that keeps track of everything you need to grab!
"""
from typing import Optional, List
from .storage import GrabbitStore, GrabbitItem, default_store


class Grabbit:
    """Your friendly shopping list rabbit 🐰
    
    Grabbit helps you track:
    - Things you need to buy
    - Where to buy them (stores)
    - Who they're for (gifts!)
    - What's urgent vs. nice-to-have
    """

    # Category aliases for flexible input
    CATEGORY_ALIASES = {
        "grocery": "groceries",
        "food": "groceries",
        "home": "household",
        "house": "household",
        "clothes": "clothing",
        "apparel": "clothing",
        "tech": "electronics",
        "gadget": "electronics",
        "gift": "gifts",
        "present": "gifts",
    }

    # Store aliases for common stores
    STORE_ALIASES = {
        "amazon": "Amazon",
        "costco": "Costco",
        "target": "Target",
        "walmart": "Walmart",
        "whole foods": "Whole Foods",
        "wholefoods": "Whole Foods",
        "trader joes": "Trader Joe's",
        "traderjoes": "Trader Joe's",
        "tj": "Trader Joe's",
        "safeway": "Safeway",
        "cvs": "CVS",
        "walgreens": "Walgreens",
        "home depot": "Home Depot",
        "homedepot": "Home Depot",
        "lowes": "Lowe's",
        "ikea": "IKEA",
        "nordstrom": "Nordstrom",
        "rei": "REI",
    }

    def __init__(self, store: GrabbitStore = None):
        self.store = store or default_store

    def _normalize_category(self, category: str) -> str:
        """Normalize category name."""
        cat = category.lower().strip()
        return self.CATEGORY_ALIASES.get(cat, cat)

    def _normalize_store(self, store: str) -> str:
        """Normalize store name."""
        store_lower = store.lower().strip()
        return self.STORE_ALIASES.get(store_lower, store)

    # ─────────────────────────────────────────────────────────────
    # Adding items
    # ─────────────────────────────────────────────────────────────

    def add(self,
            item: str,
            store: Optional[str] = None,
            category: str = "other",
            for_person: str = "self",
            notes: Optional[str] = None,
            priority: str = "medium",
            url: Optional[str] = None,
            price: Optional[float] = None,
            recurring: bool = False,
            source: str = "manual") -> dict:
        """Add an item to grab 🐰
        
        Args:
            item: What you need to buy (e.g., "oat milk", "birthday gift for Sowmya")
            store: Where to buy it (optional) - e.g., "Costco", "Amazon"
            category: Type of item - groceries|household|clothing|electronics|gifts|other
            for_person: Who it's for - "self" or name like "Sowmya", "Riaan"
            notes: Extra details (e.g., "the organic kind", "size medium")
            priority: How urgent - low|medium|high|urgent
            url: Link to the item online (optional)
            price: Estimated or known price (optional)
            recurring: Is this something you buy regularly?
            source: Where this came from - manual|google_keep|whatsapp
            
        Returns:
            The created item
            
        Examples:
            grabbit.add("oat milk")
            grabbit.add("diapers", store="Costco", priority="urgent")
            grabbit.add("Kindle", for_person="Sowmya", category="gifts", notes="She mentioned wanting one")
        """
        # Normalize inputs
        if store:
            store = self._normalize_store(store)
        category = self._normalize_category(category)
        
        # Create and save the item
        new_item = GrabbitItem.create(
            item=item,
            store=store,
            category=category,
            for_person=for_person,
            notes=notes,
            priority=priority,
            url=url,
            price=price,
            recurring=recurring,
            source=source,
        )
        
        result = self.store.add(new_item)
        return {
            "success": True,
            "message": f"🐰 Grabbed! Added '{item}'" + (f" ({store})" if store else ""),
            "item": result
        }

    # ─────────────────────────────────────────────────────────────
    # Listing & filtering
    # ─────────────────────────────────────────────────────────────

    def list(self,
             status: str = "needed",
             store: Optional[str] = None,
             category: Optional[str] = None,
             for_person: Optional[str] = None,
             priority: Optional[str] = None) -> dict:
        """List items to grab 🐰
        
        Args:
            status: Filter by status - needed|bought|archived|all
            store: Filter by store (e.g., "Costco")
            category: Filter by category
            for_person: Filter by who it's for
            priority: Filter by priority
            
        Returns:
            List of matching items
            
        Examples:
            grabbit.list()  # All needed items
            grabbit.list(store="Costco")  # What to grab at Costco
            grabbit.list(for_person="Sowmya")  # Gift ideas for Sowmya
            grabbit.list(priority="urgent")  # Urgent items
        """
        # Normalize inputs
        if store:
            store = self._normalize_store(store)
        if category:
            category = self._normalize_category(category)
        
        # Handle "all" status
        actual_status = None if status == "all" else status
        
        items = self.store.list_all(
            status=actual_status,
            store=store,
            category=category,
            for_person=for_person,
            priority=priority
        )
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        items.sort(key=lambda x: priority_order.get(x.get("priority", "medium"), 2))
        
        return {
            "count": len(items),
            "items": items,
            "filters": {
                "status": status,
                "store": store,
                "category": category,
                "for_person": for_person,
                "priority": priority
            }
        }

    def at_store(self, store: str) -> dict:
        """What do I need to grab at this store? 🐰
        
        Shortcut for list(store=X, status="needed")
        """
        return self.list(store=store, status="needed")

    def for_person(self, person: str) -> dict:
        """What gift ideas do I have for this person? 🐰"""
        return self.list(for_person=person, status="needed")

    def urgent(self) -> dict:
        """What's urgent to grab? 🐰"""
        return self.list(priority="urgent", status="needed")

    def search(self, query: str) -> dict:
        """Search for items by name or notes 🐰"""
        items = self.store.search(query)
        return {
            "query": query,
            "count": len(items),
            "items": items
        }

    def stores(self) -> dict:
        """List all stores with items 🐰"""
        stores = self.store.get_stores()
        result = {}
        for store in stores:
            items = self.store.list_all(status="needed", store=store)
            result[store] = len(items)
        return {
            "stores": result,
            "total_stores": len(stores)
        }

    # ─────────────────────────────────────────────────────────────
    # Updating items
    # ─────────────────────────────────────────────────────────────

    def mark_bought(self, item_id: str = None, item_name: str = None) -> dict:
        """Mark an item as bought 🐰
        
        Can use either item_id or search by item_name.
        """
        if item_id:
            result = self.store.mark_bought(item_id)
            if result:
                return {
                    "success": True,
                    "message": f"🐰 Nice grab! Marked '{result['item']}' as bought.",
                    "item": result
                }
        elif item_name:
            # Find by name
            items = self.store.search(item_name)
            needed = [i for i in items if i.get("status") == "needed"]
            if len(needed) == 1:
                result = self.store.mark_bought(needed[0]["id"])
                return {
                    "success": True,
                    "message": f"🐰 Nice grab! Marked '{result['item']}' as bought.",
                    "item": result
                }
            elif len(needed) > 1:
                return {
                    "success": False,
                    "message": f"🐰 Found {len(needed)} items matching '{item_name}'. Be more specific or use the ID.",
                    "matches": needed
                }
        
        return {
            "success": False,
            "message": "🐰 Couldn't find that item!"
        }

    def archive(self, item_id: str) -> dict:
        """Archive an item (remove from active list without deleting) 🐰"""
        result = self.store.archive(item_id)
        if result:
            return {
                "success": True,
                "message": f"🐰 Archived '{result['item']}'",
                "item": result
            }
        return {
            "success": False,
            "message": "🐰 Couldn't find that item!"
        }

    def delete(self, item_id: str) -> dict:
        """Permanently delete an item 🐰"""
        # Get item name first
        item = self.store.get(item_id)
        if item and self.store.delete(item_id):
            return {
                "success": True,
                "message": f"🐰 Deleted '{item['item']}'"
            }
        return {
            "success": False,
            "message": "🐰 Couldn't find that item!"
        }

    def update(self, item_id: str, **updates) -> dict:
        """Update an item's details 🐰"""
        # Normalize any category/store updates
        if "category" in updates:
            updates["category"] = self._normalize_category(updates["category"])
        if "store" in updates:
            updates["store"] = self._normalize_store(updates["store"])
            
        result = self.store.update(item_id, **updates)
        if result:
            return {
                "success": True,
                "message": f"🐰 Updated '{result['item']}'",
                "item": result
            }
        return {
            "success": False,
            "message": "🐰 Couldn't find that item!"
        }

    # ─────────────────────────────────────────────────────────────
    # Stats & history
    # ─────────────────────────────────────────────────────────────

    def recent_purchases(self, days: int = 7) -> dict:
        """What did I grab recently? 🐰"""
        items = self.store.get_recent_purchases(days)
        return {
            "days": days,
            "count": len(items),
            "items": items
        }

    def summary(self) -> dict:
        """Get a summary of the shopping list 🐰"""
        all_items = self.store.list_all()
        needed = [i for i in all_items if i.get("status") == "needed"]
        bought = [i for i in all_items if i.get("status") == "bought"]
        
        # Count by category
        categories = {}
        for item in needed:
            cat = item.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Count urgent
        urgent = len([i for i in needed if i.get("priority") == "urgent"])
        
        return {
            "total_needed": len(needed),
            "total_bought": len(bought),
            "urgent": urgent,
            "by_category": categories,
            "stores": self.stores()["stores"]
        }


# Default tracker instance
grabbit = Grabbit()
