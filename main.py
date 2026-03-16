import os
import sys
import json
import logging
import argparse
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Resolve paths absolutely to support cron jobs
BASE_DIR = Path(__file__).resolve().parent
SECRETS_FILE = BASE_DIR / 'secrets.env'
STATE_FILE = BASE_DIR / 'sync_state.json'

# Load environment variables
load_dotenv(SECRETS_FILE)

# Setup Notion Client
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')
notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# Optional: Set a default icon URL for all pages
PAGE_ICON_URL = None

def load_state():
    """Loads the list of already synced item IDs to prevent duplicates."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'last_sync_time': None, 'synced_ids': {}}

def save_state(state):
    """Saves state atomically to prevent corruption if the script crashes mid-write."""
    fd, temp_path = tempfile.mkstemp(dir=BASE_DIR)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(state, f, indent=4)
        os.replace(temp_path, STATE_FILE)
    except Exception as e:
        os.unlink(temp_path)
        logging.error(f"Failed to save state: {e}")
        raise

def add_to_notion(properties, children=None, cover_url=None, icon_url=None):
    """Universal wrapper to push a formatted page to the Notion database."""
    if not notion:
        logging.error("Notion client not initialized. Check your NOTION_TOKEN.")
        return False
        
    page_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
    }
    
    if children:
        page_data["children"] = children
        
    if icon_url:
        page_data["icon"] = {"type": "external", "external": {"url": icon_url}}
        
    if cover_url:
        page_data["cover"] = {"type": "external", "external": {"url": cover_url}}

    try:
        notion.pages.create(**page_data)
        return True
    except Exception as e:
        logging.error(f"Error adding page to Notion: {e}")
        return False

# ==========================================
# PROJECT SPECIFIC LOGIC GOES BELOW
# ==========================================

def fetch_data(limit=None):
    """
    TODO: Fetch data from your specific source (Reddit, GitHub API, ProductHunt, etc.)
    Returns a list of dictionaries/objects.
    """
    return []

def format_notion_properties(item):
    """
    TODO: Map the raw item to Notion properties.
    Returns: (unique_id, properties_dict, cover_url, page_children)
    """
    unique_id = str(item.get('id'))
    properties = {
        "Name": {"title": [{"text": {"content": "Sample Item Title"}}]},
        # Add other specific database properties here
    }
    return unique_id, properties, None, []

# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Universal Sync to Notion Boilerplate")
    parser.add_argument('-l', '--limit', type=int, help="Limit the number of items to fetch (useful for testing).")
    args = parser.parse_args()
    
    logging.info("Starting Sync to Notion...")
    
    if not DATABASE_ID or not NOTION_TOKEN:
        logging.error("Missing Notion credentials in secrets.env.")
        sys.exit(1)
        
    state = load_state()
    synced_ids_dict = state.get('synced_ids', {})
    
    # 1. Fetch the raw data
    items = fetch_data(limit=args.limit)
    
    # 2. Process oldest first if you want them chronologically ordered in Notion
    # items.reverse() 
    
    new_sync_count = 0
    current_sync_time = datetime.utcnow().isoformat()
    
    for item in items:
        # 3. Format the data for Notion
        item_id, properties, cover_url, children = format_notion_properties(item)
        
        # 4. Skip if already synced
        if not item_id or item_id in synced_ids_dict:
            continue
            
        logging.info(f"Processing item {item_id}...")
        
        # 5. Push to Notion
        success = add_to_notion(properties, children=children, cover_url=cover_url, icon_url=PAGE_ICON_URL)
        
        if success:
            synced_ids_dict[item_id] = current_sync_time
            new_sync_count += 1
            logging.info(f"Successfully synced item {item_id}.")
        else:
            logging.warning(f"Failed to sync item {item_id}.")
            
    # 6. Save progress
    state['synced_ids'] = synced_ids_dict
    state['last_sync_time'] = current_sync_time
    save_state(state)
    
    logging.info(f"Sync complete! Synced {new_sync_count} new items.")

if __name__ == '__main__':
    main()
