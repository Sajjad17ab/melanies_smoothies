import requests
import json

# Tableau Cloud login credentials
username = 'your_username'
password = 'your_password'
site = 'your_site_name'  # Can be left empty for the default site
tableau_server_url = 'https://10ay.online.tableau.com'  # Modify according to your region

# API endpoint for Tableau authentication
auth_url = f"{tableau_server_url}/api/3.10/auth/signin"

# Request payload for authentication
payload = {
    "credentials": {
        "name": username,
        "password": password,
        "site": {
            "contentUrl": site
        }
    }
}

# Headers for API request
headers = {
    "Content-Type": "application/json"
}

# Make POST request to authenticate
response = requests.post(auth_url, json=payload, headers=headers)

# Check if authentication was successful
if response.status_code == 200:
    auth_token = response.json()['credentials']['token']
    site_id = response.json()['credentials']['site']['id']
    print("Successfully authenticated!")
    print(f"Auth Token: {auth_token}")
    print(f"Site ID: {site_id}")
else:
    print("Authentication failed!")
    print(f"Error: {response.text}")
