"""
Clear Notion Data
=================
This script deletes ALL data from the configured Notion databases:
- Activities
- Daily Steps
- Sleep Data

This allows for a fresh sync of historical data.
WARNING: This action is irreversible.

Usage:
    python clear_notion_data.py
"""

import os
from notion_client import Client
from dotenv import load_dotenv
import time

def delete_all_pages(client, database_id, db_name):
    """Delete all pages in a Notion database."""
    print(f"\n🗑️  Deleting all pages in {db_name}...")
    
    has_more = True
    start_cursor = None
    deleted_count = 0
    
    while has_more:
        try:
            response = client.databases.query(
                database_id=database_id,
                start_cursor=start_cursor,
                page_size=100
            )
            
            pages = response.get("results", [])
            has_more = response.get("has_more")
            start_cursor = response.get("next_cursor")
            
            if not pages:
                break
                
            for page in pages:
                client.pages.update(page_id=page["id"], archived=True)
                deleted_count += 1
                if deleted_count % 10 == 0:
                    print(f"   Deleted {deleted_count} pages...", end="\r")
            
            # Rate limiting check
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            break
            
    print(f"   ✅ Deleted {deleted_count} pages in {db_name}")

def main():
    load_dotenv()
    
    # Get environment variables
    notion_token = os.getenv("NOTION_TOKEN")
    activities_db = os.getenv("NOTION_DB_ID")
    steps_db = os.getenv("NOTION_STEPS_DB_ID")
    sleep_db = os.getenv("NOTION_SLEEP_DB_ID")
    
    if not notion_token:
        print("❌ Missing NOTION_TOKEN in .env")
        return

    print("=" * 50)
    print("⚠️  DANGER: CLEAR ALL NOTION DATA")
    print("=" * 50)
    print("This script will PERMANENTLY DELETE all data in your linked Notion databases.")
    print("Databases to be cleared:")
    if activities_db: print(f" - Activities ({activities_db})")
    if steps_db: print(f" - Daily Steps ({steps_db})")
    if sleep_db: print(f" - Sleep Data ({sleep_db})")
    print("-" * 50)
    
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Operation cancelled.")
        return
        
    client = Client(auth=notion_token)
    
    if activities_db:
        delete_all_pages(client, activities_db, "Activities")
    
    if steps_db:
        delete_all_pages(client, steps_db, "Daily Steps")
        
    if sleep_db:
        delete_all_pages(client, sleep_db, "Sleep Data")
        
    print("\n" + "=" * 50)
    print("✅ All data cleared. You can now run the historical sync.")
    print("=" * 50)

if __name__ == '__main__':
    main()
