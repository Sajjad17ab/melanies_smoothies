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

# If the user selects "Create Schedules"
elif option == "Create Schedules":
    if st.button("Create Schedules"):
        if token_name and token_value and server_url:
            try:
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                with server.auth.sign_in(tableau_auth):
                    # Check if the current user is a system administrator
                    current_user = server.users.get_by_id(server.auth.token)
                    user_roles = [role.name for role in current_user.roles]
                    if "Server Administrator" not in user_roles:
                        st.error("You do not have the necessary permissions (Server Administrator) to create schedules.")
                    else:
                        # Hourly Schedule
                        hourly_interval = TSC.HourlyInterval(start_time=time(2, 30), end_time=time(23, 0), interval_value=2)
                        hourly_schedule = TSC.ScheduleItem(
                            "Hourly-Schedule",
                            50,
                            TSC.ScheduleItem.Type.Extract,
                            TSC.ScheduleItem.ExecutionOrder.Parallel,
                            hourly_interval,
                        )
                        hourly_schedule = server.schedules.create(hourly_schedule)
                        st.write(f"Hourly schedule created (ID: {hourly_schedule.id}).")

                        # Daily Schedule
                        daily_interval = TSC.DailyInterval(start_time=time(5))
                        daily_schedule = TSC.ScheduleItem(
                            "Daily-Schedule",
                            60,
                            TSC.ScheduleItem.Type.Subscription,
                            TSC.ScheduleItem.ExecutionOrder.Serial,
                            daily_interval,
                        )
                        daily_schedule = server.schedules.create(daily_schedule)
                        st.write(f"Daily schedule created (ID: {daily_schedule.id}).")

                        # Weekly Schedule
                        weekly_interval = TSC.WeeklyInterval(time(19, 15), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Wednesday, TSC.IntervalItem.Day.Friday)
                        weekly_schedule = TSC.ScheduleItem(
                            "Weekly-Schedule",
                            70,
                            TSC.ScheduleItem.Type.Extract,
                            TSC.ScheduleItem.ExecutionOrder.Serial,
                            weekly_interval,
                        )
                        weekly_schedule = server.schedules.create(weekly_schedule)
                        st.write(f"Weekly schedule created (ID: {weekly_schedule.id}).")

                        # Monthly Schedule
                        monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
                        monthly_schedule = TSC.ScheduleItem(
                            "Monthly-Schedule",
                            80,
                            TSC.ScheduleItem.Type.Subscription,
                            TSC.ScheduleItem.ExecutionOrder.Parallel,
                            monthly_interval,
                        )
                        monthly_schedule = server.schedules.create(monthly_schedule)
                        st.write(f"Monthly schedule created (ID: {monthly_schedule.id}).")

            except Exception as e:
                st.error(f"An error occurred while creating the schedules: {e}")
        else:
            st.error("Please provide all the necessary credentials.")
