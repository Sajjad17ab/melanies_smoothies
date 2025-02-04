import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import logging
import os
from datetime import time
from tableauserverclient import ServerResponseError


# Streamlit UI for user credentials input
st.title("Tableau Admin Task Automation : Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Radio button to switch between create project, content info, publish workbook, and create group
option = st.radio("Select an option:", ("Content Info", "Create Project", "Publish Workbook", "Create Group"))

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
                    # Get the list of users
                    all_users, pagination_item = server.users.get()

                    # Get the list of datasources
                    all_datasources, pagination_item_ds = server.datasources.get()

                    # Get the list of workbooks
                    all_workbooks_items, pagination_item_wb = server.workbooks.get()

                    # Combine all the data into one DataFrame for users
                    users_df = pd.DataFrame([(user.id, user.name) for user in all_users], columns=["ID", "Name"])
                    users_df["Type"] = "User"  # Add a 'Type' column indicating that this data is about users

                    # Combine all the data into one DataFrame for datasources
                    datasources_df = pd.DataFrame([(datasource.id, datasource.name) for datasource in all_datasources], columns=["ID", "Name"])
                    datasources_df["Type"] = "Datasource"  # Add a 'Type' column indicating that this data is about datasources

                    # Combine all the data into one DataFrame for workbooks
                    workbooks_df = pd.DataFrame([(workbook.id, workbook.name) for workbook in all_workbooks_items], columns=["ID", "Name"])
                    workbooks_df["Type"] = "Workbook"  # Add a 'Type' column indicating that this data is about workbooks

                    # Concatenate all data into one DataFrame
                    combined_df = pd.concat([users_df, datasources_df, workbooks_df], ignore_index=True)

                    # Display the combined DataFrame in a table format
                    st.write(f"There are {combined_df.shape[0]} total entries:")
                    st.dataframe(combined_df)  # Display the combined table in Streamlit app

                    # Function to convert DataFrame to Excel
                    def to_excel(df):
                        # Create a BytesIO object and write the DataFrame to it as an Excel file
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Tableau Data")
                        output.seek(0)  # Rewind the buffer to the beginning
                        return output

                    # Add a radio button to let users choose the export format
                    export_option = st.radio("Choose export format:", ("Excel", "CSV"))

                    # Based on the selected export option, prepare the file for download
                    if export_option == "Excel":
                        excel_file = to_excel(combined_df)
                        st.download_button(
                            label="Download Excel file",
                            data=excel_file,
                            file_name="tableau_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif export_option == "CSV":
                        csv_data = combined_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV file",
                            data=csv_data,
                            file_name="tableau_data.csv",
                            mime="text/csv"
                        )

            except Exception as e:
                st.error(f"An error occurred while connecting to Tableau: {e}")
        else:
            st.error("Please provide all the necessary credentials.")

# If the user selects "Create Project"
elif option == "Create Project":
    # Ask for project name and description if the user selects "Create Project"
    project_name = st.text_input("Enter the Project Name")
    project_description = st.text_area("Enter Project Description")

    # Button to create the project
    if st.button("Create Project"):
        if project_name and project_description:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    # Create a new project on Tableau Server
                    top_level_project = TSC.ProjectItem(
                        name=project_name,
                        description=project_description,
                        content_permissions=None,
                        parent_id=None,
                    )

                    # Create the project
                    created_project = server.projects.create(top_level_project)
                    st.success(f"Project '{created_project.name}' created successfully!")

            except Exception as e:
                st.error(f"An error occurred while creating the project: {e}")
        else:
            st.error("Please provide both project name and description.")

# If the user selects "Publish Workbook"
elif option == "Publish Workbook":
    # Ask for project name if the user selects "Publish Workbook"
    project_name = st.text_input("Enter the project name where the workbook should be published")

    # File uploader to upload the workbook file
    uploaded_file = st.file_uploader("Choose a workbook file", type=["twb", "twbx"])

    # Button to publish the workbook
    if st.button("Publish Workbook"):
        if uploaded_file and project_name:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    # Retrieve project ID by name
                    req_options = TSC.RequestOptions()
                    req_options.filter.add(
                        TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name)
                    )
                    projects = list(TSC.Pager(server.projects, req_options))
                    if len(projects) > 1:
                        raise ValueError("The project name is not unique")
                    project_id = projects[0].id

                    # Save the uploaded file to a temporary location
                    file_path = "/tmp/" + uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Define connections (example connections for demo purposes)
                    connection1 = TSC.ConnectionItem()
                    connection1.server_address = "mssql.test.com"
                    connection1.connection_credentials = TSC.ConnectionCredentials("test", "password", True)

                    connection2 = TSC.ConnectionItem()
                    connection2.server_address = "postgres.test.com"
                    connection2.server_port = "5432"
                    connection2.connection_credentials = TSC.ConnectionCredentials("test", "password", True)

                    all_connections = [connection1, connection2]

                    # Define workbook item
                    overwrite_true = TSC.Server.PublishMode.Overwrite
                    new_workbook = TSC.WorkbookItem(
                        project_id=project_id,
                        name=uploaded_file.name.split('.')[0],  # Use the uploaded file's name as workbook name
                        show_tabs=True
                    )

                    # Publish the workbook
                    new_workbook = server.workbooks.publish(
                        new_workbook,
                        file_path,
                        overwrite_true,
                        connections=all_connections
                    )

                    st.success(f"Workbook '{new_workbook.name}' published successfully!")
            except Exception as e:
                st.error(f"An error occurred while publishing the workbook: {e}")
        else:
            st.error("Please provide the uploaded file and project name.")

# If the user selects "Create Group"
elif option == "Create Group":
    # Ask for group name
    group_name = st.text_input("Enter the Group Name")

    # File uploader for users CSV file (optional)
    users_file = st.file_uploader("Upload CSV file with user information (optional)", type="csv")

    # Button to create the group
    if st.button("Create Group"):
        if group_name:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    # Create a new group
                    group = TSC.GroupItem(group_name)
                    try:
                        group = server.groups.create(group)
                    except TSC.server.endpoint.exceptions.ServerResponseError as rError:
                        if rError.code == "409009":  # Group already exists
                            st.warning("Group already exists.")
                            group = server.groups.filter(name=group.name)[0]
                        else:
                            raise rError

                    # If users CSV file is uploaded, add users to the group
                    if users_file:
                        filepath = os.path.abspath(users_file.name)
                        st.write(f"Adding users from file {filepath}:")
                        added, failed = server.users.create_from_file(filepath)

                        for user, error in failed:
                            if error.code == "409017":  # User already exists
                                user = server.users.filter(name=user.name)[0]
                                added.append(user)

                        for user in added:
                            try:
                                server.groups.add_user(group, user.id)
                                st.write(f"User {user.name} added to group {group.name}")
                            except ServerResponseError as serverError:
                                if serverError.code == "409011":  # User already in group
                                    st.write(f"User {user.name} is already a member of group {group.name}")
                                else:
                                    raise serverError

                    st.success(f"Group '{group_name}' created successfully!")
            except Exception as e:
                st.error(f"An error occurred while creating the group: {e}")
        else:
            st.error("Please provide a group name.")
