import streamlit as st
import requests

# Streamlit title
st.title("Tableau Cloud Login with Personal Access Token (PAT)")

# User input for Tableau Cloud credentials
st.subheader("Enter Tableau Cloud Credentials")

# Tableau Personal Access Token (PAT) details input
token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) Name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) Value", type="password")
site = st.text_input("Enter your Tableau Site Name (leave empty for default site)", "")

# Tableau Cloud URL input
cloud_url = st.text_input("Enter your Tableau Cloud URL (e.g., https://10ay.online.tableau.com)", "")

# API version
api_version = "3.10"  # You can change the version if needed
auth_url = f"{cloud_url}/api/{api_version}/auth/signin"

# Function to authenticate user to Tableau Cloud
def authenticate_to_tableau():
    payload = {
        "credentials": {
            "name": token_name,
            "password": token_value,
            "site": {
                "contentUrl": site
            }
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Send POST request to authenticate
        response = requests.post(auth_url, json=payload, headers=headers)

        if response.status_code == 200:
            st.success("Login successful!")
            response_data = response.json()
            token = response_data["credentials"]["token"]
            site_name = response_data["credentials"]["site"]["contentUrl"]
            user_name = response_data["credentials"]["user"]["name"]

            st.write(f"Authenticated User: {user_name}")
            st.write(f"Authenticated Site: {site_name}")
            st.write(f"Authentication Token: {token}")

            return token  # Return token for further API calls
        else:
            st.error(f"Login failed! Status code: {response.status_code}")
            error_message = response.json().get("error", {}).get("detail", "Unknown error")
            st.write(f"Error: {error_message}")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while authenticating: {e}")

# Button to trigger the login
if st.button("Login to Tableau Cloud"):
    if token_name and token_value and cloud_url:
        authenticate_to_tableau()
    else:
        st.error("Please fill in all required fields.")
