import requests
import os
import warnings
from dotenv import load_dotenv

def load_environment_variables():
    """Reload .env file to ensure updated environment variables."""
    load_dotenv(override=True)

# Load the .env file initially
load_environment_variables()
API_TOKEN = os.getenv("API_TOKEN")
NEW_IP_ADDRESS = os.getenv("NEW_IP_ADDRESS")

if not API_TOKEN:
    raise ValueError("API_TOKEN not found in .env file")

if not NEW_IP_ADDRESS:
    raise ValueError("NEW_IP_ADDRESS not found in .env file")

print(f"Loaded API_TOKEN: {API_TOKEN}")
print(f"Loaded NEW_IP_ADDRESS: {NEW_IP_ADDRESS}")


BASE_URL = "https://api.cloudflare.com/client/v4"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}

def get_zones():
    """Fetch all zones (domains) in the Cloudflare account with pagination."""
    url = f"{BASE_URL}/zones"
    zones = []
    page = 1

    while True:
        params = {"page": page, "per_page": 50}  # Adjust `per_page` if needed
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        zones.extend(data["result"])

        # Check if there are more pages
        result_info = data.get("result_info", {})
        if result_info.get("page", 1) >= result_info.get("total_pages", 1):
            break

        page += 1

    return zones


def get_dns_records(zone_id):
    """Fetch all DNS records for a given zone."""
    url = f"{BASE_URL}/zones/{zone_id}/dns_records"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["result"]

def create_a_record(zone_id, record_name):
    """Create a new A record with the specified IP address."""
    url = f"{BASE_URL}/zones/{zone_id}/dns_records"
    payload = {
        "type": "A",
        "name": record_name,
        "content": NEW_IP_ADDRESS,
        "ttl": 60,  # Auto TTL
        "proxied": False  # Set to True to enable Cloudflare proxy
    }
    try:
        print(f"Creating A record: {record_name} with payload: {payload}")
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"API Response: {result}")
        return result["success"]
    except requests.exceptions.RequestException as e:
        print(f"Error creating record {record_name}: {e}")
        return False


def update_a_record(zone_id, record_id, record_name):
    """Update an A record with a new IP address."""
    url = f"{BASE_URL}/zones/{zone_id}/dns_records/{record_id}"
    payload = {
        "type": "A",
        "name": record_name,
        "content": NEW_IP_ADDRESS,
        "ttl": 60,  # Auto TTL
        "proxied": False  # Set to True to enable Cloudflare proxy
    }
    try:
        print(f"Updating {record_name} with payload: {payload}")
        response = requests.put(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"API Response: {result}")
        return result["success"]
    except requests.exceptions.RequestException as e:
        print(f"Error updating record {record_name}: {e}")
        return False


def main():
    try:
        print("Fetching zones...")
        zones = get_zones()

        print("Select the domains you want to update:")
        for i, zone in enumerate(zones):
            print(f"[{i}] {zone['name']}")

        selected_indices = input("Enter the numbers of the domains to update, separated by commas: ")
        selected_indices = [int(idx.strip()) for idx in selected_indices.split(",")]

        for idx in selected_indices:
            if idx < 0 or idx >= len(zones):
                print(f"Invalid selection: {idx}")
                continue

            zone = zones[idx]
            zone_id = zone["id"]
            zone_name = zone["name"]
            print(f"Processing zone: {zone_name} ({zone_id})")

            dns_records = get_dns_records(zone_id)
            updated = False

            for record in dns_records:
                if record["type"] == "A":
                    record_id = record["id"]
                    record_name = record["name"]

                    if record["content"] == NEW_IP_ADDRESS:
                        print(f"A record {record_name} already points to {NEW_IP_ADDRESS}. Skipping update.")
                        updated = True
                        continue

                    print(f"Updating A record: {record_name} ({record_id})")
                    success = update_a_record(zone_id, record_id, record_name)

                    if success:
                        print(f"Successfully updated {record_name} to {NEW_IP_ADDRESS}")
                    else:
                        print(f"Failed to update {record_name}")
                    updated = True

            # If no matching record was updated, create a new A record
            if not updated:
                print(f"No A records to update for zone {zone_name}. Creating a new A record.")
                new_record_name = input(f"Enter the subdomain for the new A record (e.g., 'www' for www.{zone_name}): ")
                new_record_name = f"{new_record_name}.{zone_name}" if new_record_name else zone_name
                success = create_a_record(zone_id, new_record_name)

                if success:
                    print(f"Successfully created A record {new_record_name} pointing to {NEW_IP_ADDRESS}")
                else:
                    print(f"Failed to create A record {new_record_name}")

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
