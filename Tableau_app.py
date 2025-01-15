import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import os
import logging
from datetime import time

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Streamlit UI for user credentials input
st.title("Tableau Automation with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Dropdown to switch between create project, content info, publish workbook, create group, and create schedules
option = st.selectbox("Select an option:", ["Content Info", "Create Project", "Publish Workbook", "Create Group"])
# New Code to check
import tableauserverclient as TSC

def make_filter(**kwargs):
    """Helper function to create a filter for the API requests."""
    options = TSC.RequestOptions()
    for item, value in kwargs.items():
        name = getattr(TSC.RequestOptions.Field, item)
        options.filter.add(TSC.Filter(name, TSC.RequestOptions.Operator.Equals, value))
    return options

def get_workbook_by_name(server, name):
    """Fetches a workbook by its name."""
    request_filter = make_filter(Name=name)
    workbooks, _ = server.workbooks.get(request_filter)
    assert len(workbooks) == 1, f"Workbook {name} not found or multiple workbooks found."
    return workbooks.pop()

def get_datasource_by_name(server, name):
    """Fetches a datasource by its name."""
    request_filter = make_filter(Name=name)
    datasources, _ = server.datasources.get(request_filter)
    assert len(datasources) == 1, f"Datasource {name} not found or multiple datasources found."
    return datasources.pop()

def get_flow_by_name(server, name):
    """Fetches a flow by its name."""
    request_filter = make_filter(Name=name)
    flows, _ = server.flows.get(request_filter)
    assert len(flows) == 1, f"Flow {name} not found or multiple flows found."
    return flows.pop()

def get_schedule_by_name(server, name):
    """Fetches a schedule by its name."""
    schedules = [x for x in TSC.Pager(server.schedules) if x.name == name]
    assert len(schedules) == 1, f"Schedule {name} not found or multiple schedules found."
    return schedules.pop()

def assign_to_schedule(server, workbook_or_datasource, schedule):
    """Assign a workbook or datasource to a schedule."""
    server.schedules.add_to_schedule(schedule.id, workbook_or_datasource)
How to Use It in Your Main Code
Ensure that you integrate these functions properly into your workflow. Here's a modified section that includes calling get_workbook_by_name and assigning it to the correct schedule:

python
Copy code
import logging
import tableauserverclient as TSC

def refresh_workbook_or_datasource(token_name, token_value, site_id, server_url, resource_type, resource_id, schedule_name):
    """Function to refresh a workbook or datasource with a specific schedule."""
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()

    try:
        # Authentication and server connection
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
        server = TSC.Server(server_url, use_server_version=True)
        
        with server.auth.sign_in(tableau_auth):
            # Determine the resource to refresh based on user input (workbook, datasource, etc.)
            if resource_type == "workbook":
                item = get_workbook_by_name(server, resource_id)
            elif resource_type == "datasource":
                item = get_datasource_by_name(server, resource_id)
            else:
                raise ValueError("Invalid resource type specified.")
            
            # Get the schedule by name
            schedule = get_schedule_by_name(server, schedule_name)
            
            # Assign the item (workbook/datasource) to the selected schedule
            assign_to_schedule(server, item, schedule)
            
            logger.info(f"Successfully assigned {resource_type} '{resource_id}' to schedule '{schedule_name}'.")
            return True
    except Exception as e:
        logger.error(f"An error occurred while refreshing the workbook/datasource: {str(e)}")
        return False

# Example usage
refresh_workbook_or_datasource(
    token_name="your_token_name", 
    token_value="your_token_value", 
    site_id="your_site_id", 
    server_url="https://your.tableau.server.url", 
    resource_type="workbook", 
    resource_id="your_workbook_id", 
    schedule_name="Daily Refresh"
)
# New Code End



# If the user selects "Content Info"
if option == "Content Info":
    if st.button("Connect to Tableau"):
        if token_name and token_value and server_url:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                with server.auth.sign_in(tableau_auth):
                    all_users, pagination_item = server.users.get()
                    all_datasources, pagination_item_ds = server.datasources.get()
                    all_workbooks_items, pagination_item_wb = server.workbooks.get()

                    users_df = pd.DataFrame([(user.id, user.name) for user in all_users], columns=["ID", "Name"])
                    users_df["Type"] = "User"

                    datasources_df = pd.DataFrame([(datasource.id, datasource.name) for datasource in all_datasources], columns=["ID", "Name"])
                    datasources_df["Type"] = "Datasource"

                    workbooks_df = pd.DataFrame([(workbook.id, workbook.name) for workbook in all_workbooks_items], columns=["ID", "Name"])
                    workbooks_df["Type"] = "Workbook"

                    combined_df = pd.concat([users_df, datasources_df, workbooks_df], ignore_index=True)
                    st.write(f"There are {combined_df.shape[0]} total entries:")
                    st.dataframe(combined_df)

                    def to_excel(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Tableau Data")
                        output.seek(0)
                        return output

                    export_option = st.radio("Choose export format:", ("Excel", "CSV"))

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
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please provide all the necessary credentials.")

# If the user selects "Create Project"
elif option == "Create Project":
    project_name = st.text_input("Enter the Project Name")
    project_description = st.text_area("Enter Project Description")

    if st.button("Create Project"):
        if project_name and project_description:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    top_level_project = TSC.ProjectItem(
                        name=project_name,
                        description=project_description,
                        content_permissions=None,
                        parent_id=None,
                    )

                    created_project = server.projects.create(top_level_project)
                    st.success(f"Project '{created_project.name}' created successfully!")
            except Exception as e:
                st.error(f"An error occurred while creating the project: {e}")
        else:
            st.error("Please provide both project name and description.")

# If the user selects "Publish Workbook"
elif option == "Publish Workbook":
    project_name = st.text_input("Enter the project name where the workbook should be published")
    uploaded_file = st.file_uploader("Choose a workbook file", type=["twb", "twbx"])

    if st.button("Publish Workbook"):
        if uploaded_file and project_name:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    req_options = TSC.RequestOptions()
                    req_options.filter.add(
                        TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name)
                    )
                    projects = list(TSC.Pager(server.projects, req_options))
                    if len(projects) > 1:
                        raise ValueError("The project name is not unique")
                    project_id = projects[0].id

                    file_path = "/tmp/" + uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    connection1 = TSC.ConnectionItem()
                    connection1.server_address = "mssql.test.com"
                    connection1.connection_credentials = TSC.ConnectionCredentials("test", "password", True)

                    connection2 = TSC.ConnectionItem()
                    connection2.server_address = "postgres.test.com"
                    connection2.server_port = "5432"
                    connection2.connection_credentials = TSC.ConnectionCredentials("test", "password", True)

                    all_connections = [connection1, connection2]

                    overwrite_true = TSC.Server.PublishMode.Overwrite
                    new_workbook = TSC.WorkbookItem(
                        project_id=project_id,
                        name=uploaded_file.name.split('.')[0],
                        show_tabs=True
                    )

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
    group_name = st.text_input("Enter the Group Name")
    users_file = st.file_uploader("Upload CSV file with user information (optional)", type="csv")

    if st.button("Create Group"):
        if group_name:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)
                
                with server.auth.sign_in(tableau_auth):
                    group = TSC.GroupItem(group_name)
                    try:
                        group = server.groups.create(group)
                    except TSC.server.endpoint.exceptions.ServerResponseError as rError:
                        if rError.code == "409009":  
                            st.warning("Group already exists.")
                            group = server.groups.filter(name=group.name)[0]
                        else:
                            raise rError

                    if users_file:
                        filepath = os.path.abspath(users_file.name)
                        st.write(f"Adding users from file {filepath}:")
                        added, failed = server.users.create_from_file(filepath)

                        for user, error in failed:
                            if error.code == "409017":  
                                user = server.users.filter(name=user.name)[0]
                                added.append(user)

                        for user in added:
                            try:
                                server.groups.add_user(group, user.id)
                                st.write(f"User {user.name} added to group {group.name}")
                            except TSC.ServerResponseError as serverError:
                                if serverError.code == "409011":  
                                    st.write(f"User {user.name} is already a member of group {group.name}")
                                else:
                                    raise serverError

                    st.success(f"Group '{group_name}' created successfully!")
            except Exception as e:
                st.error(f"An error occurred while creating the group: {e}")
        else:
            st.error("Please provide a group name.")
