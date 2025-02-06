import requests
import json
import os
import time
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration (from .env)
DOMAINS_FILE = "domains.txt"

def add_domain(domain):
    """Adds a domain to Cloudflare."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")  # Get from env within function to ensure reload
    ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not API_TOKEN or not ACCOUNT_ID:
        print("Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set in .env file.")
        return None

    url = f"https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "account": {"id": ACCOUNT_ID},
        "name": domain,
        "type": "full"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print(f"Added domain {domain}: {result}")
        return result.get("result", {}).get("id")
    except requests.exceptions.RequestException as e:
        print(f"Error adding domain {domain}: {e}")
        if response.status_code != 200:
            print(f"Response content: {response.text}")
        return None

def get_nameservers(zone_id):
    """Retrieves nameservers for a given zone ID."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN") # Get from env within function to ensure reload
    if not API_TOKEN:
        print("Error: CLOUDFLARE_API_TOKEN must be set in .env file.")
        return None

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        nameservers = result.get("result", {}).get("name_servers")
        print(f"Nameservers for zone ID {zone_id}: {nameservers}")
        return nameservers
    except requests.exceptions.RequestException as e:
        print(f"Error getting nameservers for zone ID {zone_id}: {e}")
        return None


class DotenvEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".env"):
            print(".env file modified. Reloading...")
            load_dotenv(override=True)
            # You might want to re-initialize parts of your app dependent on env vars here

def main():
    load_dotenv()  # Load initially
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not API_TOKEN or not ACCOUNT_ID:
        print("Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set in .env file.")
        return

    try:
        with open(DOMAINS_FILE, "r") as f:
            domains = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: Domains file '{DOMAINS_FILE}' not found.")
        return

    # Watch for .env changes (optional, comment out if not needed)
    event_handler = DotenvEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        for domain in domains:
            zone_id = add_domain(domain)
            if zone_id:
                get_nameservers(zone_id)
            time.sleep(1)  # Small delay to avoid rate limiting (adjust as needed)

        while True:  # Keep the main thread alive for the watcher (optional)
            time.sleep(1)
            # Your main application logic can go here. The .env will reload in the background
    except KeyboardInterrupt:
        observer.stop()  # Stop the watcher
    finally:
        observer.join()  # Ensure the watcher thread exits cleanly



if __name__ == "__main__":
    main()