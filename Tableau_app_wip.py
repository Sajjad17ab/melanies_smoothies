import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import StringIO

# Streamlit UI for user credentials input
st.title("Tableau Dashboard with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Radio button to switch between different options (Content Info, Download Workbook, etc.)
option = st.radio("Select an option:", ("Content Info", "Create Project", "Publish Workbook", "Create Group", "Download Workbook"))

# Function to retrieve all content (workbooks, datasources, projects, views)
def fetch_all_content():
    try:
        # Tableau authentication using Personal Access Token (PAT)
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
        server = TSC.Server(server_url, use_server_version=True)

        # Connect to Tableau Server/Online
        with server.auth.sign_in(tableau_auth):
            # Fetch workbooks
            all_workbooks, _ = server.workbooks.get()

            # Fetch datasources
            all_datasources, _ = server.datasources.get()

            # Fetch projects
            all_projects, _ = server.projects.get()

            # Fetch views
            all_views, _ = server.views.get()

            # Create an empty list to hold views and their associated workbooks
            views_data = []
            for view in all_views:
                # Get the workbook ID for this view
                workbook_id = view.workbook.id if hasattr(view, 'workbook') else None
                workbook_name = "Unknown"
                workbook_project = "Unknown"
                
                if workbook_id:
                    # Fetch the workbook by ID to get the name and project
                    workbook = server.workbooks.get_by_id(workbook_id)
                    workbook_name = workbook.name
                    workbook_project = workbook.project_name
                
                # Append view information along with its workbook info
                views_data.append((view.id, view.name, workbook_name, workbook_project))

            # Combine all content into a dictionary to display
            workbooks_data = [(workbook.id, workbook.name, workbook.project_name, workbook.size) for workbook in all_workbooks]
            datasources_data = [(datasource.id, datasource.name, datasource.project_name, datasource.size) for datasource in all_datasources]
            projects_data = [(project.id, project.name) for project in all_projects]

            # Create dataframes for each content type
            workbooks_df = pd.DataFrame(workbooks_data, columns=["ID", "Name", "Project", "Size"])
            datasources_df = pd.DataFrame(datasources_data, columns=["ID", "Name", "Project", "Size"])
            projects_df = pd.DataFrame(projects_data, columns=["ID", "Name"])
            views_df = pd.DataFrame(views_data, columns=["ID", "Name", "Workbook", "Project"])

            return workbooks_df, datasources_df, projects_df, views_df

    except Exception as e:
        st.error(f"An error occurred while retrieving content: {e}")
        return None, None, None, None


# If the user selects "Content Info"
if option == "Content Info":
    if st.button("Connect to Tableau and Fetch Content Info"):
        if token_name and token_value and server_url:
            workbooks_df, datasources_df, projects_df, views_df = fetch_all_content()

            if workbooks_df is not None:
                # Add download button for workbooks table
                csv_workbooks = workbooks_df.to_csv(index=False)
                st.download_button(
                    label="Download Workbooks CSV",
                    data=csv_workbooks,
                    file_name="workbooks.csv",
                    mime="text/csv"
                )
                st.write(f"There are {workbooks_df.shape[0]} workbooks on the server:")
                st.dataframe(workbooks_df)  # Display workbooks in a table
                
                # Add download button for datasources table
                csv_datasources = datasources_df.to_csv(index=False)
                st.download_button(
                    label="Download Datasources CSV",
                    data=csv_datasources,
                    file_name="datasources.csv",
                    mime="text/csv"
                )
                st.write(f"There are {datasources_df.shape[0]} datasources on the server:")
                st.dataframe(datasources_df)  # Display datasources in a table
                
                # Add download button for projects table
                csv_projects = projects_df.to_csv(index=False)
                st.download_button(
                    label="Download Projects CSV",
                    data=csv_projects,
                    file_name="projects.csv",
                    mime="text/csv"
                )
                st.write(f"There are {projects_df.shape[0]} projects on the server:")
                st.dataframe(projects_df)  # Display projects in a table
                
                # Add download button for views table
                csv_views = views_df.to_csv(index=False)
                st.download_button(
                    label="Download Views CSV",
                    data=csv_views,
                    file_name="views.csv",
                    mime="text/csv"
                )
                st.write(f"There are {views_df.shape[0]} views on the server:")
                st.dataframe(views_df)  # Display views in a table
            else:
                st.error("Unable to fetch content data.")

# If the user selects "Download Workbook"
elif option == "Download Workbook":
    workbook_id = st.text_input("Enter the workbook ID to download")
    
    # Button to trigger the workbook download
    if st.button("Download Workbook to Local Machine"):
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
                        label="Download Workbook Now",
                        data=file_data,
                        file_name=f"{workbook.name}.twbx",
                        mime="application/octet-stream"
                    )
                    st.success(f"Workbook '{workbook.name}' is ready for download!")

            except Exception as e:
                st.error(f"An error occurred while downloading the workbook: {e}")
        else:
            st.error("Please provide the workbook ID to download.")

# If the user selects "Publish Workbook"
elif option == "Publish Workbook":
    # Upload file and publish to Tableau
    workbook_file = st.file_uploader("Upload a workbook file (.twbx)", type=["twbx"])
    
    if st.button("Publish Workbook"):
        if workbook_file:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    # Define project to publish the workbook (you can change the project name as needed)
                    project_name = "default"  # Replace with desired project name
                    project = server.projects.get_by_name(project_name)

                    # Publish workbook
                    new_workbook = TSC.WorkbookItem(project.id, name=workbook_file.name)
                    new_workbook = server.workbooks.publish(new_workbook, workbook_file, TSC.Server.PublishMode.Overwrite)
                    
                    st.success(f"Workbook '{workbook_file.name}' published successfully to project '{project_name}'.")

            except Exception as e:
                st.error(f"An error occurred while publishing the workbook: {e}")
        else:
            st.error("Please upload a workbook file to publish.")

# If the user selects "Create Project"
elif option == "Create Project":
    project_name = st.text_input("Enter the new project name")

    if st.button("Create Project"):
        if project_name:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    # Create a new project
                    new_project = TSC.ProjectItem(name=project_name)
                    new_project = server.projects.create(new_project)

                    st.success(f"Project '{project_name}' created successfully.")

            except Exception as e:
                st.error(f"An error occurred while creating the project: {e}")
        else:
            st.error("Please provide a project name.")

# If the user selects "Create Group"
elif option == "Create Group":
    group_name = st.text_input("Enter the new group name")

    if st.button("Create Group"):
        if group_name:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    # Create a new group
                    new_group = TSC.GroupItem(name=group_name)
                    new_group = server.groups.create(new_group)

                    st.success(f"Group '{group_name}' created successfully.")

            except Exception as e:
                st.error(f"An error occurred while creating the group: {e}")
        else:
            st.error("Please provide a group name.")
