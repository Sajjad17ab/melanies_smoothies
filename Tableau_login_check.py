import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import logging


# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Radio button to switch between create project, content info, publish workbook, and download workbook
option = st.radio("Select an option:", ("Content Info", "Create Project", "Publish Workbook", "Download Workbook"))

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

                    # Convert the DataFrame to an Excel file
                    def to_excel(df):
                        # Create a BytesIO object and write the DataFrame to it as an Excel file
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Tableau Data")
                        output.seek(0)  # Rewind the buffer to the beginning
                        return output

                    # Prepare the Excel file for download
                    excel_file = to_excel(combined_df)

                    # Add a download button to allow the user to download the file
                    st.download_button(
                        label="Download Excel file",
                        data=excel_file,
                        file_name="tableau_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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

# If the user selects "Download Workbook"
elif option == "Download Workbook":
    # Ask for workbook ID
    workbook_id = st.text_input("Enter the Workbook ID")

    # Button to download the workbook
    if st.button("Download Workbook"):
        if workbook_id:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    # Get workbook by ID
                    workbook = server.workbooks.get_by_id(workbook_id)

                    # Get the workbook file as a .twbx file
                    file_path = server.workbooks.download(workbook)

                    # Prepare the file for download
                    with open(file_path, "rb") as f:
                        file_data = f.read()

                    # Provide download button for the user to download the workbook
                    st.download_button(
                        label="Download Workbook",
                        data=file_data,
                        file_name=f"{workbook.name}.twbx",
                        mime="application/octet-stream"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred while downloading the workbook: {e}")
        else:
            st.error("Please provide the workbook ID.")
