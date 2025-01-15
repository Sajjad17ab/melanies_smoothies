import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
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

# Dropdown to select an option
option = st.selectbox("Select an option:", ("Content Info", "Create Project", "Publish Workbook", "Create Group", "Create Schedules"))

# If the user selects "Content Info"
if option == "Content Info":
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

# If the user selects "Create Extract Task"
if option == "Create Extract Task":
    resource_type = st.selectbox("Select Resource Type", ("workbook", "datasource"))
    resource_id = st.text_input("Enter the Resource ID (Workbook or Datasource ID)")
    incremental = st.checkbox("Enable Incremental Refresh")

    if st.button("Create Extract Task"):
        if token_name and token_value and server_url and resource_id:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                with server.auth.sign_in(tableau_auth):
                    # Set the refresh type
                    refresh_type = "FullRefresh" if not incremental else "Incremental"

                    # Define the monthly schedule interval (15th of every month at 11:30 PM)
                    monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)

                    # Create a schedule item for the task
                    monthly_schedule = TSC.ScheduleItem(
                        None,
                        None,
                        None,
                        None,
                        monthly_interval,
                    )

                    # Retrieve the resource (workbook or datasource) by ID
                    if resource_type == "workbook":
                        resource_item = server.workbooks.get_by_id(resource_id)
                    elif resource_type == "datasource":
                        resource_item = server.datasources.get_by_id(resource_id)

                    # Create the target item (workbook or datasource)
                    target_item = TSC.Target(
                        resource_item.id,  # the ID of the workbook or datasource
                        resource_type,  # could be "workbook" or "datasource"
                    )

                    # Create the scheduled extract task
                    scheduled_extract_item = TSC.TaskItem(
                        None,
                        refresh_type,  # Refresh type (Full or Incremental)
                        None,
                        None,
                        None,
                        monthly_schedule,
                        None,
                        target_item,
                    )

                    # Create the scheduled extract task on Tableau Server
                    response = server.tasks.create(scheduled_extract_item)

                    # Display the response
                    st.success(f"Extract task created successfully: {response}")

            except Exception as e:
                st.error(f"An error occurred while creating the extract task: {e}")
        else:
            st.error("Please provide all the necessary credentials and resource ID.")
