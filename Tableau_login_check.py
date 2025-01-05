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

        # If the response is empty or not valid JSON
        if response.status_code != 200:
            st.error(f"Login failed! Status code: {response.status_code}")
            st.write(f"Response Text: {response.text}")
            return None

        # Try to parse the response content as JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            st.error("Response could not be parsed as JSON.")
            st.write(f"Raw response: {response.text}")
            return None

        # Check if the response contains valid authentication token
        if "credentials" in response_data and "token" in response_data["credentials"]:
            st.success("Login successful!")
            token = response_data["credentials"]["token"]
            site_name = response_data["credentials"]["site"]["contentUrl"]
            user_name = response_data["credentials"]["user"]["name"]

            st.write(f"Authenticated User: {user_name}")
            st.write(f"Authenticated Site: {site_name}")
            st.write(f"Authentication Token: {token}")

            return token  # Return token for further API calls
        else:
            st.error(f"Unexpected response structure. Response: {response_data}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while authenticating: {e}")
        return None

# Button to trigger the login
if st.button("Login to Tableau Cloud"):
    # Check if required fields are provided
    if token_name and token_value and cloud_url:
        token = authenticate_to_tableau()
        if token:
            st.success("You are successfully authenticated with Tableau Cloud.")
    else:
        st.error("Please enter all required fields: PAT Name, PAT Value, and Tableau Cloud URL.")
