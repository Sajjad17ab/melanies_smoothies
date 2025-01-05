import streamlit as st
import tableauserverclient as TSC
import os
import pandas as pd

# Title of the Streamlit app
st.title("Publish or Export Tableau Content to Cloud")

# OAuth Authentication Setup (You need to replace these with your actual OAuth credentials)
client_id = st.text_input("Enter your OAuth Client ID")
client_secret = st.text_input("Enter your OAuth Client Secret", type="password")
redirect_uri = st.text_input("Enter your Redirect URI")

# Authentication method selection (radio button)
auth_method = st.radio("Select Authentication Method", ("OAuth", "Personal Access Token (PAT)", "Username/Password"))

# Authentication input fields (conditional based on selected method)
if auth_method == "Username/Password":
    st.subheader("Username and Password Authentication")
    username = st.text_input("Enter your Tableau username", "")
    password = st.text_input("Enter your Tableau password", "", type="password")
elif auth_method == "Personal Access Token (PAT)":
    st.subheader("Personal Access Token (PAT) Authentication")
    token_name = st.text_input("Enter your Personal Access Token (PAT) name", "")
    token_value = st.text_input("Enter your Personal Access Token (PAT) value", "")
else:
    st.subheader("OAuth Authentication")
    # Display OAuth auth URL and instructions
    st.write("Click below to authenticate using OAuth")
    oauth_url = f"https://your-tableau-cloud-url/auth/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    st.write(f"[Authenticate with OAuth]({oauth_url})")

# Tableau Cloud URL and Site
server_url = st.text_input("Enter your Tableau Cloud URL", "https://your-tableau-cloud.com")
site = st.text_input("Enter your site name (leave empty for default)", "")

# Function to handle OAuth authentication
def oauth_authenticate(oauth_code):
    try:
        # Exchange the authorization code for an access token
        oauth_url = f"{server_url}/auth/oauth2/token"
        payload = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": oauth_code,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(oauth_url, data=payload, headers=headers)

        # Check if the response contains an access token
        if response.status_code == 200:
            oauth_data = response.json()
            access_token = oauth_data['access_token']
            st.success("OAuth Authentication successful!")
            return access_token
        else:
            st.error(f"OAuth Authentication failed! Status Code: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"An error occurred during OAuth authentication: {e}")
        return None

# Button to start OAuth authentication (after user clicks the OAuth URL)
if auth_method == "OAuth" and st.button("Complete OAuth Authentication"):
    oauth_code = st.text_input("Enter the OAuth Authorization Code")  # This will be provided after user authenticates
    if oauth_code:
        access_token = oauth_authenticate(oauth_code)
        if access_token:
            st.write(f"Access Token: {access_token}")

# Switch between Upload and Download options
mode = st.radio("Choose an option", ("Upload", "Download"))

# Function to authenticate with the provided credentials
def authenticate_to_tableau(auth_method, username=None, password=None, token_name=None, token_value=None, oauth_token=None):
    try:
        if auth_method == "Username/Password":
            if not username or not password:
                st.error("Please provide both username and password.")
                return None
            tableau_auth = TSC.TableauAuth(username, password)
        elif auth_method == "Personal Access Token (PAT)":
            if not token_name or not token_value:
                st.error("Please provide both token name and token value.")
                return None
            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value)
        elif auth_method == "OAuth":
            if not oauth_token:
                st.error("OAuth token is missing. Please complete OAuth authentication.")
                return None
            tableau_auth = TSC.OAuthAuth(oauth_token)

        server = TSC.Server(server_url, use_server_version=True)
        return tableau_auth, server
    except Exception as e:
        st.error(f"An error occurred during authentication: {e}")
        return None, None

# Use authentication details to authenticate and perform actions
if mode == "Upload":
    # Upload functionality as usual
    if st.button("Publish to Tableau Cloud"):
        tableau_auth, server = authenticate_to_tableau(auth_method, username, password, token_name, token_value, oauth_token=access_token if auth_method == "OAuth" else None)
        if tableau_auth:
            with server.auth.sign_in(tableau_auth, site=site):
                # Upload logic...
                pass

elif mode == "Download":
    # Download functionality as usual
    if st.button("Export All Content Names and Owners to CSV"):
        tableau_auth, server = authenticate_to_tableau(auth_method, username, password, token_name, token_value, oauth_token=access_token if auth_method == "OAuth" else None)
        if tableau_auth:
            with server.auth.sign_in(tableau_auth, site=site):
                # Download logic...
                pass
