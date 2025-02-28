import requests
import json
import os
import time
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration (from .env)
DOMAINS_FILE = "domains.txt"
COMPLETED_FILE = "completed.txt"
RATE_LIMIT_DELAY = 60  # Time to wait on 429 Too Many Requests

def load_completed_domains():
    """Load completed domains from file."""
    if not os.path.exists(COMPLETED_FILE):
        return set()
    with open(COMPLETED_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_completed_domain(domain):
    """Append a completed domain to the completed file."""
    with open(COMPLETED_FILE, "a") as f:
        f.write(f"{domain}\n")

def add_domain(domain):
    """Adds a domain to Cloudflare."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    if not API_TOKEN or not ACCOUNT_ID:
        print("Error: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set in .env file.")
        return None

    url = "https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "account": {"id": ACCOUNT_ID},
        "name": domain,
        "type": "full"
    }

    while True:
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            print(f"Added domain {domain}: {result}")
            save_completed_domain(domain)  # Mark as completed
            return result.get("result", {}).get("id")
        except requests.exceptions.RequestException as e:
            print(f"Error adding domain {domain}: {e}")

            try:
                error_data = response.json()
                error_message = error_data.get("errors", [{}])[0].get("message", "Unknown error")
                print(f"Response content: {error_data}")
            except json.JSONDecodeError:
                error_message = "Could not decode error message"

            if response.status_code == 429:
                print(f"Rate limit hit. {error_message} Waiting {RATE_LIMIT_DELAY} seconds...")
                time.sleep(RATE_LIMIT_DELAY)
                continue  # Retry after delay

            if response.status_code == 400:
                error_code = error_data.get("errors", [{}])[0].get("code")
                if error_code == 1061:  # Domain already exists
                    print(f"Domain {domain} already exists, skipping.")
                    save_completed_domain(domain)
                elif error_code == 1117:  # Rate limit exceeded with detailed message
                    print(f"{error_message} Stopping script.")
                    exit(1)
                elif error_code == 1118:  # Generic rate limit exceeded
                    print("Rate limit exceeded, stopping script.")
                    exit(1)
            return None

def get_nameservers(zone_id):
    """Retrieves nameservers for a given zone ID."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
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

    completed_domains = load_completed_domains()

    event_handler = DotenvEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()

    try:
        for domain in domains:
            if domain in completed_domains:
                print(f"Skipping already completed domain: {domain}")
                continue

            zone_id = add_domain(domain)
            if zone_id:
                get_nameservers(zone_id)
            time.sleep(1)  # Delay to avoid rate limiting

        while True:
            time.sleep(1)  # Keep script running for .env monitoring
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()

if __name__ == "__main__":
    main()
