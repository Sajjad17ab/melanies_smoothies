import streamlit as st
import tableauserverclient as TSC

# Streamlit UI
st.title("Tableau Login Test")

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

    except TSC.ServerResponseError as e:
        st.error(f"Server response error: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
