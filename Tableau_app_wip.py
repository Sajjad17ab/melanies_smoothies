import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import logging
import os
from datetime import time
from tableauserverclient import ServerResponseError


# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Radio button to switch between create project, content info, publish workbook, create group, or download workbook
option = st.radio("Select an option:", ("Content Info", "Create Project", "Publish Workbook", "Create Group", "Download Workbook"))

# If the user selects "Content Info"
if option == "Content Info":
    # Button to trigger the connection
    if st.button("Connect to Tableau"):
        if token_name and token_value and server_url:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    # Get the list of workbooks
                    all_workbooks_items, pagination_item_wb = server.workbooks.get()

                    # Combine all the data into one DataFrame for workbooks
                    workbooks_df = pd.DataFrame([(workbook.id, workbook.name, workbook.project_name, workbook.size) 
                                                 for workbook in all_workbooks_items], columns=["ID", "Name", "Project", "Size"])
                    
                    # Display the combined DataFrame in a table format
                    st.write(f"There are {workbooks_df.shape[0]} total workbooks:")
                    st.dataframe(workbooks_df)  # Display the combined table in Streamlit app

            except Exception as e:
                st.error(f"An error occurred while connecting to Tableau: {e}")
        else:
            st.error("Please provide all the necessary credentials.")

# If the user selects "Download Workbook"
elif option == "Download Workbook":
    # Ask for the workbook ID (which will be used to download the workbook)
    workbook_id = st.text_input("Enter the workbook ID to download")
    
    # Button to trigger the workbook download
    if st.button("Download Workbook"):
        if workbook_id:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    # Get the workbook by ID
                    workbook = server.workbooks.get_by_id(workbook_id)
                    
                    # Define a path where to save the workbook (can be adjusted as per requirement)
                    save_path = f"/tmp/{workbook.name}.twbx"  # Save the workbook as a .twbx file

                    # Download the workbook
                    file_data = server.workbooks.download(workbook.id)

                    # Offer the workbook as a downloadable file
                    st.download_button(
                        label="Download Workbook",
                        data=file_data,
                        file_name=f"{workbook.name}.twbx",
                        mime="application/octet-stream"
                    )
                    st.success(f"Workbook '{workbook.name}' is ready for download!")

            except Exception as e:
                st.error(f"An error occurred while downloading the workbook: {e}")
        else:
            st.error("Please provide the workbook ID to download.")

# Additional options for creating projects, publishing workbooks, etc., go here.
# The rest of your code remains unchanged
