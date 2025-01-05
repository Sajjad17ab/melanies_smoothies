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

            # Get the server information
            server_info = server_connection.server_info
            st.write(f"Server Info: {server_info}")

            # If the version is included in the server_info, access it via the json() method or attributes.
            if hasattr(server_info, 'version'):
                st.write(f"Tableau Server Version: {server_info.version}")
            else:
                # If there's no 'version' directly, attempt to parse from the json()
                st.write("Unable to retrieve the version directly. Server Info: ", server_info.json())

    except TSC.ServerResponseError as e:
        st.error(f"Server response error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
