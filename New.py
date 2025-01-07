import streamlit as st
import tableauserverclient as TSC

# Function to refresh the extract for a data source
def refresh_data_source_extract(data_source_id):
    try:
        # Tableau authentication using Personal Access Token (PAT)
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
        server = TSC.Server(server_url, use_server_version=True)

        # Connect to Tableau Server/Online
        with server.auth.sign_in(tableau_auth):
            # Fetch the data source by ID
            data_source = server.datasources.get_by_id(data_source_id)
            
            # Trigger the extract refresh
            server.datasources.refresh(data_source)

            # Inform the user
            st.success(f"Extract refresh triggered successfully for Data Source: {data_source.name}")
    
    except Exception as e:
        st.error(f"An error occurred while refreshing the data source extract: {e}")

# UI components in Streamlit
st.title("Tableau Data Source Extract Refresh")

# Get user credentials and data source ID
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Ask for the Data Source ID to refresh the extract
data_source_id = st.text_input("Enter the Data Source ID to refresh its extract")

# Button to trigger the refresh
if st.button("Refresh Data Source Extract"):
    if data_source_id:
        refresh_data_source_extract(data_source_id)
    else:
        st.error("Please enter a valid Data Source ID.")
