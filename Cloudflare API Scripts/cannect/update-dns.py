import requests
import json
import os
import time
from dotenv import load_dotenv

# Configuration (from .env)
DOMAINS_FILE = "domains.txt"

def update_dns_records(domain, ip_address):
    """Updates DNS records for a domain in Cloudflare."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    ZONE_ID = get_zone_id(domain)  # Get zone ID based on domain
    if not API_TOKEN or not ZONE_ID:
        print(f"Error: CLOUDFLARE_API_TOKEN or ZONE_ID not found for {domain}.")
        return

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # Update or create A record for root domain
        update_or_create_record(ZONE_ID, headers, domain, ip_address)

        # Update or create A record for www subdomain
        update_or_create_record(ZONE_ID, headers, f"www.{domain}", ip_address)

    except requests.exceptions.RequestException as e:
        print(f"Error updating DNS records for {domain}: {e}")

def get_zone_id(domain):
    """Retrieves the zone ID for a domain."""
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    if not API_TOKEN:
        print("Error: CLOUDFLARE_API_TOKEN must be set in .env file.")
        return None

    url = f"https://api.cloudflare.com/client/v4/zones"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        zones = response.json().get("result", [])

        for zone in zones:
            if zone.get("name") == domain:
                return zone.get("id")

        print(f"Zone ID not found for domain: {domain}")
        return None  # Return None if the domain is not found

    except requests.exceptions.RequestException as e:
        print(f"Error getting zone ID for {domain}: {e}")
        return None

def update_or_create_record(zone_id, headers, name, ip_address):
    """Updates or creates a DNS record."""

    # Check if a record with the same name exists
    existing_record_id = None
    records_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    try:
        records_response = requests.get(records_url, headers=headers)
        records_response.raise_for_status()
        existing_records = records_response.json().get("result", [])
        for record in existing_records:
            if record.get("name") == name and record.get("type") == "A":
                existing_record_id = record.get("id")
                break
    except requests.exceptions.RequestException as e:
        print(f"Error checking for existing records for {name}: {e}")
        return

    data = {
        "type": "A",
        "name": name,
        "content": ip_address,
        "ttl": 60,
        "proxied": False
    }

    if existing_record_id:
        # Update existing record
        url = f"{records_url}/{existing_record_id}"
        method = requests.put
        print(f"Updating A record for {name}")

    else:
        # Create new record
        url = records_url
        method = requests.post
        print(f"Creating A record for {name}")


    response = method(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"DNS update/creation for {name}: {response.json()}")



def main():
    load_dotenv()
    API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    IP_ADDRESS = os.getenv("NEW_IP_ADDRESS")  # New IP address from .env

    if not API_TOKEN or not IP_ADDRESS:
        print("Error: CLOUDFLARE_API_TOKEN and NEW_IP_ADDRESS must be set in .env file.")
        return

    try:
        with open(DOMAINS_FILE, "r") as f:
            domains = [line.strip() for line in f]
    except FileNotFoundError:
        print(f"Error: Domains file '{DOMAINS_FILE}' not found.")
        return

    for domain in domains:
        update_dns_records(domain, IP_ADDRESS)
        time.sleep(1)  # Small delay to avoid rate limiting



if __name__ == "__main__":
    main()