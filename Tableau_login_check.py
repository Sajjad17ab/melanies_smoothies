import tableauserverclient as TSC
import streamlit as st

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
    try:
        # Create authentication object using PersonalAccessTokenAuth
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site if site else None)
        server = TSC.Server(server_url, use_server_version=True)

        # Attempt login
        with server.auth.sign_in(tableau_auth):
            st.success("Login successful!")
            st.write("You are now logged in to Tableau Cloud.")
        
    except Exception as e:
        st.error(f"Login failed: {e}")
