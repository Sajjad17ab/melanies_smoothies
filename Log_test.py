import streamlit as st
import tableauserverclient as TSC

# Streamlit UI
st.title("Tableau Login Test - Detailed Information")

# Input fields for server details
server = st.text_input("Server address")
site = st.text_input("Site name")
token_name = st.text_input("Personal Access Token name")
token_value = st.text_input("Personal Access Token value", type="password")

# Action button to trigger the login test
if st.button("Test Login"):
    # Tableau Authentication
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site)
    server_connection = TSC.Server(server, use_server_version=True, http_options={"verify": False})

    try:
        # Attempt to sign in
        with server_connection.auth.sign_in(tableau_auth):
            st.write("Connected to Tableau Server successfully!")

            # Display authentication details
            st.write(f"Authenticated with site: {site}")
            st.write(f"Using token: {token_name}")

            # Get and display the server information
            server_info = server_connection.server_info

            # Displaying product version, build number, and REST API version
            st.write(f"Tableau Product Version: {server_info.product_version}")
            st.write(f"Tableau Build Number: {server_info.build_number}")
            st.write(f"REST API Version: {server_info.rest_api_version}")

    except TSC.ServerResponseError as e:
        st.error(f"Server response error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
