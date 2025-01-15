import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import os
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT) or Username/Password")

# Choose Authentication method (PAT or Username/Password)
auth_method = st.radio("Select Authentication Method", ["Personal Access Token (PAT)", "Username/Password"])

if auth_method == "Personal Access Token (PAT)":
    # Credentials for Personal Access Token (PAT)
    token_name = st.text_input("Enter your Tableau Personal Access Token Name (if using PAT)")
    token_value = st.text_input("Enter your Tableau Personal Access Token Value (if using PAT)", type="password")
    site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
    server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

elif auth_method =="Username/Password":
    # Credentials for Username/Password Authentication
    username = st.text_input("Enter your Tableau Username (if using Username/Password)")
    password = st.text_input("Enter your Tableau Password (if using Username/Password)", type="password")
    site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
    server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Dropdown to switch between create project, content info, publish workbook, and create group
option = st.selectbox("Select an option:", ["Content Info", "Create Project", "Publish Workbook", "Create Group"])

# If the user selects "Content Info"
if option == "Content Info":
    if st.button("Connect to Tableau"):
        if auth_method == "Personal Access Token (PAT)" and token_name and token_value and server_url:
            try:
                # Tableau authentication using Personal Access Token (PAT)
                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    logger.info("Successfully signed in to Tableau Server (PAT)!")
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

            except TSC.ServerResponseError as e:
                logger.error(f"Error signing in to Tableau: {e}")
                st.error(f"An error occurred: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                st.error(f"An unexpected error occurred: {e}")
        elif auth_method == "Username/Password" and username and password and server_url:
            try:
                # Tableau authentication using Username and Password
                tableau_auth = TSC.TableauAuth(username, password, site=site_id)
                server = TSC.Server(server_url, use_server_version=True)

                # Connect to Tableau Server/Online
                with server.auth.sign_in(tableau_auth):
                    logger.info("Successfully signed in to Tableau Server (Username/Password)!")
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

            except TSC.ServerResponseError as e:
                logger.error(f"Error signing in to Tableau: {e}")
                st.error(f"An error occurred: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.error("Please provide the necessary credentials for authentication.")

# Handle other options (Create Project, Publish Workbook, Create Group) similarly
# ... (Continue as before for Create Project, Publish Workbook, and Create Group options)

