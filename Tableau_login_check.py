import streamlit as st
import requests
import json

# Title of the Streamlit app
st.title("Tableau Online Login and Fetch Projects")

# User input fields for Tableau Online Authentication (PAT)
st.subheader("Authentication to Tableau Online")

token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) Name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) Value", type="password")
site = st.text_input("Enter your Tableau Site Name (leave empty for default)", "")

# Define server URL for Tableau Online
server_url = "https://<your-site-name>.online.tableau.com"  # Replace with your actual Tableau Online site URL

# Authentication API URL
auth_url = f"{server_url}/api/3.10/auth/signin"

# Function to login to Tableau Online
def login_to_tableau_online():
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
        # Make POST request to authenticate
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
            st.error(f"Login failed. Status code: {response.status_code}")
            st.write(f"Response Text: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

# Button to trigger the login
if st.button("Login to Tableau Online"):
    # Check if required fields are provided
    if token_name and token_value:
        token = login_to_tableau_online()
        
        if token:
            # Use the token to get additional info like projects
            projects_url = f"{server_url}/api/3.10/sites/{site}/projects"
            headers = {
                "X-Tableau-Auth": token
            }

            try:
                # Get the list of projects
                projects_response = requests.get(projects_url, headers=headers)

                if projects_response.status_code == 200:
                    projects_data = projects_response.json()
                    projects = projects_data.get('projects', {}).get('project', [])
                    if projects:
                        st.write("List of Projects on Tableau Online:")
                        for project in projects:
                            st.write(f"Project Name: {project['name']}")
                    else:
                        st.write("No projects found.")
                else:
                    st.error(f"Failed to fetch projects. Status code: {projects_response.status_code}")
                    st.write(f"Response Text: {projects_response.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter both the PAT Name and PAT Value.")
