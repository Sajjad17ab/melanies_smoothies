import streamlit as st
import tableauserverclient as TSC

# Streamlit UI
st.title("Tableau View Exporter - Login & Upload")

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

            # Get the server information (ServerInfoItem)
            server_info = server_connection.server_info

            # Access attributes from the server_info object
            product_version = server_info.product_version
            build_number = server_info.build_number
            rest_api_version = server_info.rest_api_version

            # Displaying the information
            st.write(f"Tableau Product Version: {product_version}")
            st.write(f"Tableau Build Number: {build_number}")
            st.write(f"REST API Version: {rest_api_version}")

    except TSC.ServerResponseError as e:
        st.error(f"Server response error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
