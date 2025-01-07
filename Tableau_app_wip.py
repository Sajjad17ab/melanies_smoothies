import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO

# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Radio button to switch between create project, content info, publish workbook, create group, or download workbook
option = st.radio("Select an option:", ("Content Info", "Download Workbook"))

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

                    # Get the list of datasources
                    all_datasources_items, pagination_item_ds = server.datasources.get()

                    # Get the list of views
                    all_views_items, pagination_item_vw = server.views.get()

                    # Get the list of projects
                    all_projects_items, pagination_item_proj = server.projects.get()

                    # Combine workbooks data into DataFrame
                    workbooks_df = pd.DataFrame([(workbook.id, workbook.name, workbook.project_name, workbook.size)
                                                 for workbook in all_workbooks_items], columns=["ID", "Name", "Project", "Size"])

                    # Combine datasources data into DataFrame
                    datasources_df = pd.DataFrame([(datasource.id, datasource.name, datasource.project_name, datasource.type)
                                                   for datasource in all_datasources_items], columns=["ID", "Name", "Project", "Type"])

                    # Combine views data into DataFrame
                    views_df = pd.DataFrame([(view.id, view.name, view.workbook.name) for view in all_views_items], columns=["ID", "View Name", "Workbook"])

                    # Combine projects data into DataFrame
                    projects_df = pd.DataFrame([(project.id, project.name) for project in all_projects_items], columns=["Project ID", "Project Name"])

                    # Merge all dataframes into one
                    all_data_df = pd.concat([workbooks_df, datasources_df, views_df], axis=0, ignore_index=True)

                    # Display the combined table
                    st.write(f"There are {all_data_df.shape[0]} total records combined from workbooks, datasources, and views:")
                    st.dataframe(all_data_df)

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
                    server.workbooks.download(workbook.id, filepath=save_path)

                    # Inform the user that the download was successful
                    st.success(f"Workbook '{workbook.name}' downloaded successfully!")
                    st.write(f"File saved at: {save_path}")

            except Exception as e:
                st.error(f"An error occurred while downloading the workbook: {e}")
        else:
            st.error("Please provide the workbook ID to download.")
