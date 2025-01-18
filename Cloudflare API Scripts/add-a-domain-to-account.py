import requests
import os
from dotenv import load_dotenv

def load_environment_variables():
    """Reload .env file to ensure updated environment variables."""
    load_dotenv(override=True)

# Load the .env file initially
load_environment_variables()
API_TOKEN = os.getenv("API_TOKEN")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")
NEW_IP_ADDRESS = os.getenv("NEW_IP_ADDRESS")
TTL = int(os.getenv("TTL", 60))
PROXIED = os.getenv("PROXIED", "False").lower() == "true"

if not API_TOKEN:
    raise ValueError("API_TOKEN not found in .env file")

if not DOMAIN_NAME:
    raise ValueError("DOMAIN_NAME not found in .env file")

if not NEW_IP_ADDRESS:
    raise ValueError("NEW_IP_ADDRESS not found in .env file")

print(f"Loaded API_TOKEN: {API_TOKEN}")
print(f"Loaded DOMAIN_NAME: {DOMAIN_NAME}")
print(f"Loaded NEW_IP_ADDRESS: {NEW_IP_ADDRESS}")
print(f"Loaded TTL: {TTL}")
print(f"Loaded PROXIED: {PROXIED}")

def get_cloudflare_headers():
    """Returns the headers required for Cloudflare API requests."""
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

def get_zone_id(domain_name):
    """Retrieve the zone ID for a given domain."""
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = get_cloudflare_headers()
    params = {"name": domain_name}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['success'] and data['result']:
            return data['result'][0]['id']
        elif data['success'] and not data['result']:
            print(f"Domain '{domain_name}' does not exist in your account. Attempting to add the domain...")
            return add_domain_to_account(domain_name)
        else:
            raise ValueError(f"Failed to retrieve zone ID: {data.get('errors', data)}")
    else:
        raise ValueError(f"Error getting zone ID: {response.status_code} {response.text}")

def add_domain_to_account(domain_name):
    """Add a new domain to the Cloudflare account."""
    url = "https://api.cloudflare.com/client/v4/zones"
    headers = get_cloudflare_headers()
    payload = {
        "name": domain_name,
        "account": {"id": os.getenv("ACCOUNT_ID")},
        "jump_start": True
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"Domain '{domain_name}' added successfully.")
            return data['result']['id']
        else:
            raise ValueError(f"Failed to add domain: {data.get('errors', data)}")
    else:
        raise ValueError(f"Error adding domain: {response.status_code} {response.text}")

def create_dns_record(zone_id, domain_name, ip_address, ttl, proxied):
    """Create a DNS A record for the specified domain."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = get_cloudflare_headers()
    payload = {
        "type": "A",
        "name": domain_name,
        "content": ip_address,
        "ttl": ttl,
        "proxied": proxied
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"DNS record created successfully for {domain_name} -> {ip_address}")
        else:
            raise ValueError(f"Failed to create DNS record: {data.get('errors', data)}")
    else:
        raise ValueError(f"Error creating DNS record: {response.status_code} {response.text}")

try:
    # Get zone ID
    print("Fetching zone ID...")
    zone_id = get_zone_id(DOMAIN_NAME)
    print(f"Zone ID for {DOMAIN_NAME}: {zone_id}")

    # Create DNS record
    print("Creating DNS record...")
    create_dns_record(zone_id, DOMAIN_NAME, NEW_IP_ADDRESS, TTL, PROXIED)
except Exception as e:
    print(f"An error occurred: {e}")
