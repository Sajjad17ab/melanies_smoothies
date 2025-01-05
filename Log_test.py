import streamlit as st
import tableauserverclient as TSC
import logging
import os

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

    except TSC.exceptions.ServerResponseError as e:
        st.error(f"Login failed: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

# Upload workbook
st.subheader("Upload Workbook or Data Source")

# File uploader for Workbook or Data Source
uploaded_file = st.file_uploader("Choose a workbook or data source", type=["twb", "twbx", "tds", "tdsx"])

# Input for the project name where the file will be uploaded
project_name = st.text_input("Project Name (where to upload)")

# Action button to upload the file
if uploaded_file and project_name:
    # Set up logging
    logging.basicConfig(level=getattr(logging, logging_level.upper()))

    try:
        # Attempt to sign in again if the session expired
        with server_connection.auth.sign_in(tableau_auth):
            st.write("Reconnected to Tableau Server for upload.")
            
            # Get the project by name
            all_projects, pagination_item = server_connection.projects.get()
            project = None
            for p in all_projects:
                if p.name == project_name:
                    project = p
                    break
            
            if not project:
                st.error(f"Project '{project_name}' not found.")
            else:
                # Save the uploaded file to a temporary location
                with open(f"/tmp/{uploaded_file.name}", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                file_path = f"/tmp/{uploaded_file.name}"

                # Check if the uploaded file is a workbook or data source
                if file_path.endswith(('.twb', '.twbx')):
                    # Upload a Workbook
                    st.write(f"Uploading workbook {uploaded_file.name}...")
                    new_workbook = server_connection.workbooks.publish(
                        file_path, uploaded_file.name, project.id, connection_credentials=None
                    )
                    st.success(f"Workbook '{new_workbook.name}' uploaded successfully.")

                elif file_path.endswith(('.tds', '.tdsx')):
                    # Upload a Data Source
                    st.write(f"Uploading data source {uploaded_file.name}...")
                    new_datasource = server_connection.datasources.publish(
                        file_path, uploaded_file.name, project.id, connection_credentials=None
                    )
                    st.success(f"Data source '{new_datasource.name}' uploaded successfully.")

                # Clean up the uploaded file after the upload
                os.remove(file_path)

    except Exception as e:
        st.error(f"An error occurred during upload: {str(e)}")
