# Notion Automation Starter
    
A simple, production-ready boilerplate for automatically syncing any external data source (think Reddit posts, GitHub repositories, Spotify albums, etc.) into a Notion database. 
    
It handles all the heavy lifting--like API pagination state, atomic file writes, and Notion SDK wrapping--so you can focus entirely on writing the logic to fetch and format your data.
    
---
    
## What's Included Out of the Box?
    
- **State Management:** A local `sync_state.json` file remembers exactly which items have been synced, preventing duplicate Notion pages across consecutive runs.
- **Atomic File Writes:** State updates are saved using atomic `tempfile` replacements, meaning your progress won't corrupt even if the script crashes or the server loses power mid-write.
- **Cron-Safe Execution:** Uses `pathlib` for absolute path resolution. You can trigger this script from anywhere via `cron` or systemd without encountering "file not found" errors.
- **Batch Testing:** Includes a built-in command line argument parser (`--limit` or `-l`) so you can test formatting on 5 items before accidentally importing 5,000.
- **Universal Notion Wrapper:** A clean `add_to_notion()` function handles the official `notion-client` SDK, pushing formatted properties, page covers, custom icons, and child blocks instantly.
- **Automated Logging:** Swaps messy `print()` statements for standard Python `logging` with timestamps, making background job monitoring clean and easy.
    
---
    
## How to Build a New Automation
    
When starting a new project (e.g., syncing your Reddit saved posts), clone the repo and follow these steps:
    
**1. Define Your Data Source** 
	Open `main.py` and scroll down to the `fetch_data(limit=None)` function. Write your logic to pull data from your target API (e.g., PRAW for Reddit). Make sure it respects the `limit` argument if provided. 
    
**2. Format Your Notion Database**
	Go to `format_notion_properties(item)` and map the raw JSON fields from your source into Notion's property structure. 
* *Example:* Map `item.title` to the `Name` property, and `item.author` to a `Rich Text` property. 
* Don't forget to extract a unique ID (like a post ID) so the script knows how to track it. 
    
**3. Add Custom Icons (Optional)**
	If you want Notion pages to use specific icons (e.g., the Reddit logo), set the `PAGE_ICON_URL` constant at the top of the file to a public CDN link.
    
 ---
    
## Setup & Installation
    
**1. Create a Virtual Environment**
    Keep your dependencies isolated from your system Python.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # (On Windows use: venv\Scripts\activate)```
    

**2. Install Dependencies**
    
    
    pip install -r requirements.txt
    

_(If your project requires external libraries like `PyGithub` or `praw`, `pip install` them and add them to this file.)_

**3. Configure Secrets** 
Copy the `.env.example` file:
    
    
    cp secrets.env.example secrets.env
    

Open `secrets.env` and add:

- `NOTION_TOKEN`: Your internal integration secret (Starts with `ntn_...`).
- `DATABASE_ID`: The ID of the specific Notion database you are targeting.
- _Any other API keys your specific source requires._
* * *

## Usage

**Test Run (Recommended)** 
Before importing all your saved Reddit posts that you’ve been amassing since junior high, pull just a handful of items to verify your Notion database properties align with the data formatting:
    
    python3 main.py --limit 5
    
**Full Sync** 
Once you are happy with the formatting, run the script without limits. It will fetch all items, skip everything already listed in `sync_state.json`, and intelligently push the net-new items to Notion.
    
    python3 main.py
