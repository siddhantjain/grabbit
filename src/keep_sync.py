#!/usr/bin/env python3
"""Sync Google Keep grocery list to Grabbit 🐰"""
import os
import subprocess
import json
from pathlib import Path

# Google Doc ID (Keep synced doc)
GROCERY_DOC_ID = "1AqtjWII-A6Tdwnnil6PXtMkCaPapEvA85FUAL2do6RI"

def get_keep_items():
    """Fetch items from Google Keep (via synced Doc)."""
    # Set up environment
    env = os.environ.copy()
    env['GOG_KEYRING_PASSWORD'] = 'VwjPCa/jdhDLyCuep7PiQOuDe8Onzrv1iYJ8DEROqgs='
    env['GOG_ACCOUNT'] = 'post.siddhant@gmail.com'
    
    # Download doc as text
    result = subprocess.run(
        ['gog', 'drive', 'download', GROCERY_DOC_ID, '--format', 'txt', '--out', '/tmp/grocery_sync.txt'],
        env=env, capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Error fetching doc: {result.stderr}")
        return []
    
    # Parse items
    content = Path('/tmp/grocery_sync.txt').read_text()
    items = []
    seen = set()
    
    for line in content.split('\n'):
        # Clean line
        item = line.strip().strip('*').strip()
        
        # Skip empty, header, dividers
        if not item or item == 'grocery' or item.startswith('_'):
            continue
        
        # Skip already seen (dedup)
        if item.lower() in seen:
            continue
        
        seen.add(item.lower())
        items.append(item)
    
    return items


def categorize_item(item: str) -> str:
    """Guess category from item name."""
    item_lower = item.lower()
    
    household_keywords = ['soap', 'towel', 'scrub', 'floss', 'batteries', 'bags', 'brush', 'cleaner', 'sponge']
    if any(kw in item_lower for kw in household_keywords):
        return 'household'
    
    return 'groceries'


def sync():
    """Sync Keep items to Grabbit."""
    from tracker import grabbit
    
    print("🐰 Syncing from Google Keep...")
    
    # Get current Grabbit items (from Keep)
    current = grabbit.list(status='all')
    keep_items = {i['item'].lower(): i for i in current['items'] if i.get('source') == 'google_keep'}
    
    # Get Keep items
    new_items = get_keep_items()
    
    added = 0
    for item in new_items:
        # Skip if already in Grabbit (from Keep)
        if item.lower() in keep_items:
            continue
        
        # Add new item
        category = categorize_item(item)
        result = grabbit.add(item, category=category, source='google_keep')
        if result['success']:
            added += 1
            print(f"  + {item}")
    
    print(f"✅ Sync complete! Added {added} new items.")
    return added


if __name__ == '__main__':
    sync()
