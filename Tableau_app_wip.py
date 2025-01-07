import streamlit as st
import tableauserverclient as TSC
import pandas as pd

# Streamlit UI for user credentials input
st.title("Tableau Workbook Details")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Input for workbook ID
workbook_id = st.text_input("Enter the Workbook ID to retrieve details")

# Button to fetch workbook details
if st.button("Get Workbook Details"):
    if token_name and token_value and server_url and workbook_id:
        try:
            # Tableau authentication using Personal Access Token (PAT)
            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
            server = TSC.Server(server_url, use_server_version=True)

            with server.auth.sign_in(tableau_auth):
                # Fetch workbook details by ID
                workbook = server.workbooks.get_by_id(workbook_id)

                # Fetch the workbook's project information
                project = server.projects.get_by_id(workbook.project_id)
                
                # Fetch the workbook's views
                views, pagination_item = server.views.get(workbook)
                
                # Display workbook details
                st.subheader("Workbook Details:")
                st.write(f"**Name**: {workbook.name}")
                st.write(f"**ID**: {workbook.id}")
                st.write(f"**Created at**: {workbook.created_at}")
                st.write(f"**Modified at**: {workbook.updated_at}")
                st.write(f"**Owner**: {workbook.owner_id}")
                st.write(f"**Project**: {project.name}")
                st.write(f"**Project ID**: {project.id}")
                st.write(f"**Content URL**: {workbook.content_url}")
                st.write(f"**Description**: {workbook.description}")
                st.write(f"**Tags**: {', '.join(workbook.tags)}")

                # Display views associated with the workbook
                st.subheader("Workbook Views:")
                views_list = [(view.id, view.name) for view in views]
                views_df = pd.DataFrame(views_list, columns=["View ID", "View Name"])
                st.dataframe(views_df)

                # Fetch data sources linked to the workbook
                datasources, pagination_item = server.datasources.get(workbook)
                st.subheader("Data Sources Linked to Workbook:")
                datasources_list = [(ds.id, ds.name) for ds in datasources]
                datasources_df = pd.DataFrame(datasources_list, columns=["Datasource ID", "Datasource Name"])
                st.dataframe(datasources_df)

        except Exception as e:
            st.error(f"An error occurred while retrieving workbook details: {e}")
    else:
        st.error("Please provide all the necessary credentials and workbook ID.")

