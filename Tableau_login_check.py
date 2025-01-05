import streamlit as st
import requests
import json

# Title of the Streamlit app
st.title("Tableau Cloud Login")

# User input fields for Tableau Authentication (PAT)
st.subheader("Authentication to Tableau Cloud")

# Input for Tableau Cloud credentials
token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) Name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) Value", type="password")
site = st.text_input("Enter your Tableau Site Name (leave empty for default)", "")

# Input for Tableau Cloud URL
cloud_url = st.text_input("Enter your Tableau Cloud URL (e.g., https://10ay.online.tableau.com)", "")

# Authentication API URL
auth_url = f"{cloud_url}/api/3.10/auth/signin"

# Function to authenticate to Tableau Cloud
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

        # Debugging: print the response content
        st.write(f"Response Status Code: {response.status_code}")
        st.write(f"Response Content: {response.text}")

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
    # Check if required fields are provided
    if token_name and token_value and cloud_url:
        token = authenticate_to_tableau()
        if token:
            st.success("You are successfully authenticated with Tableau Cloud.")
    else:
        st.error("Please enter all required fields: PAT Name, PAT Value, and Tableau Cloud URL.")
