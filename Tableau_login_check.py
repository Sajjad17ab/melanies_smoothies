import streamlit as st
import requests
import json


# Title of the Streamlit app
st.title("Tableau Online Login")

# Input fields for Tableau Online login using Personal Access Token (PAT)
st.subheader("Authenticate to Tableau Online")

# Input fields for PAT and site information
token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) Name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) Value", type="password")
site = st.text_input("Enter your Tableau Site Name (leave empty for default)", "")
cloud_url = st.text_input("Enter your Tableau Online Cloud URL (e.g., https://10ay.online.tableau.com)", "")

# Authentication API URL
def get_auth_url(cloud_url):
    return f"{cloud_url}/api/3.10/auth/signin"

# Function to authenticate to Tableau Online and get the authentication token
def authenticate_to_tableau():
    if not token_name or not token_value or not cloud_url:
        st.error("Please provide all the required fields: Token Name, Token Value, and Cloud URL.")
        return None

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
        # Send a POST request to authenticate
        auth_url = get_auth_url(cloud_url)
        response = requests.post(auth_url, json=payload, headers=headers)

        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            st.success("Login successful!")

            # Parse the response JSON
            response_data = response.json()

            # Extract the authentication token and other info
            token = response_data["credentials"]["token"]
            site_name = response_data["credentials"]["site"]["contentUrl"]
            user_name = response_data["credentials"]["user"]["name"]

            # Display authenticated information
            st.write(f"Authenticated User: {user_name}")
            st.write(f"Authenticated Site: {site_name}")
            st.write(f"Authentication Token: {token}")

            return token  # Return the token for further API calls

        else:
            st.error(f"Login failed with status code {response.status_code}")
            st.write(f"Error message: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred during authentication: {e}")
        return None


# Trigger the login function when the button is clicked
if st.button("Login to Tableau Online"):
    token = authenticate_to_tableau()

    if token:
        st.write("You can now use the authentication token for further API requests.")
    else:
        st.write("Authentication failed. Please check your inputs and try again.")
