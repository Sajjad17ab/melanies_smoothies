import streamlit as st
import tableauserverclient as TSC
import logging

# Streamlit UI
st.title("Tableau View Exporter - Login & Upload")

# Input fields for server details
server = st.text_input("Server address")
site = st.text_input("Site name")
token_name = st.text_input("Personal Access Token name")
token_value = st.text_input("Personal Access Token value", type="password")

# Logging level (optional)
logging_level = st.selectbox("Logging level", ["debug", "info", "error"])

# Action button to trigger the login test
if st.button("Test Login"):
    # Set up logging
    logging.basicConfig(level=getattr(logging, logging_level.upper()))

    # Tableau Authentication
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site)
    server_connection = TSC.Server(server, use_server_version=True, http_options={"verify": False})

    try:
        # Attempt to sign in
        with server_connection.auth.sign_in(tableau_auth):
            st.write("Connected to Tableau Server successfully!")
            # Optionally, show the server version as confirmation
            server_info = server_connection.server_info
            st.write(f"Connected to Tableau Server version: {server_info.version}")

    except TSC.exceptions.TableauAuthException as e:
        st.error(f"Authentication failed: {str(e)}")
    except TSC.exceptions.ServerResponseError as e:
        st.error(f"Server response error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
