import streamlit as st
import requests
import json

# Streamlit app title
st.title("Tableau Cloud Login Check")

# User input fields for Tableau Cloud credentials
token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) value", type="password")
site = st.text_input("Enter your Tableau site name (leave empty for default)", "")

# Tableau Cloud server URL (for Cloud, it's typically a specific URL for your Tableau Cloud instance)
server_url = st.text_input("Enter your Tableau Cloud server URL", "https://your-tableau-cloud-server.com")

# Button to trigger login
if st.button("Login to Tableau Cloud"):
    if not server_url or not token_name or not token_value:
        st.error("Please fill in all required fields.")
    else:
        # Build the authentication URL
        auth_url = f"{server_url}/api/3.10/auth/signin"
        
        # Construct the payload for authentication
        payload = {
            "credentials": {
                "name": token_name,
                "password": token_value,
                "site": {
                    "contentUrl": site if site else ""
                }
            }
        }
        
        # Set headers for the request
        headers = {
            "Content-Type": "application/json"
        }

        try:
            # Send the POST request to sign in
            response = requests.post(auth_url, json=payload, headers=headers)
            
            # Debugging: Log the response status code and content
            st.write(f"Response Status Code: {response.status_code}")
            st.write(f"Response Text: {response.text}")
            
            # Check if the response is empty or if the status code is not 200
            if response.status_code != 200:
                st.error(f"Login failed: {response.status_code}. Response: {response.text}")
            else:
                # Try to parse the response JSON
                response_data = response.json()
                if "credentials" in response_data:
                    st.success("Login successful!")
                    # You can extract and display user details here
                    user = response_data["credentials"]["user"]
                    st.write(f"Welcome, {user['name']}!")
                else:
                    st.error("Unexpected response format: Missing 'credentials' key.")
                    
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred with the request: {e}")
        except json.JSONDecodeError:
            st.error("Failed to parse the response as JSON.")
