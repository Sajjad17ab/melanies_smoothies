import requests
import json

# Tableau Cloud Authentication URL
tableau_url = "https://10ay.online.tableau.com"  # Replace with your Tableau Cloud URL
api_version = "3.10"  # Replace with the correct API version
auth_url = f"{tableau_url}/api/{api_version}/auth/signin"

# Your Tableau Personal Access Token (PAT) details
token_name = "your_token_name"  # Replace with your token name
token_value = "your_token_value"  # Replace with your token value
site = ""  # Leave empty for the default site

# Payload to authenticate
payload = {
    "credentials": {
        "name": token_name,
        "password": token_value,
        "site": {
            "contentUrl": site
        }
    }
}

# Headers for the request
headers = {
    "Content-Type": "application/json"
}

# Send POST request to authenticate
response = requests.post(auth_url, json=payload, headers=headers)

# Check if authentication was successful
if response.status_code == 200:
    print("Login successful!")
    # Extract token and site details
    response_data = response.json()
    token = response_data["credentials"]["token"]
    site_name = response_data["credentials"]["site"]["contentUrl"]
    user_name = response_data["credentials"]["user"]["name"]
    
    print(f"Authenticated User: {user_name}")
    print(f"Authenticated Site: {site_name}")
    print(f"Authentication Token: {token}")
else:
    print("Login failed!")
    error_message = response.json().get("error", {}).get("detail", "Unknown error")
    print(f"Error: {error_message}")
