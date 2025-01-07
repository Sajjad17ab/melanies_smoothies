import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO
import os

# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Button to trigger the connection
if st.button("Connect to Tableau"):
    if token_name and token_value and site_id and server_url:
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

                # -----------------------------
                # File Upload Section for Workbook, Datasource, and Flow
                st.subheader("Upload Files to Tableau")

                # File upload for Workbook, Datasource, or Flow
                file = st.file_uploader("Choose a file to upload", type=["twb", "twbx", "tds", "tdsx", "tfl", "tflx"])

                if file is not None:
                    file_name = file.name
                    file_extension = file_name.split('.')[-1]

                    # Temporary path to save the uploaded file
                    temp_file_path = os.path.join("/tmp", file_name)

                    # Save the file to a temporary location
                    with open(temp_file_path, "wb") as temp_file:
                        temp_file.write(file.getbuffer())

                    # Check the file type and upload accordingly
                    if file_extension in ['twb', 'twbx']:  # Workbook file types
                        # Create a WorkbookItem to upload
                        new_workbook = TSC.WorkbookItem(name=file_name)
                        new_workbook = server.workbooks.publish(new_workbook, temp_file_path, TSC.Server.PublishMode.CreateNew)
                        st.success(f"Workbook '{file_name}' uploaded successfully!")
                    
                    elif file_extension in ['tds', 'tdsx']:  # Datasource file types
                        # Create a DatasourceItem to upload
                        new_datasource = TSC.DatasourceItem(name=file_name)
                        new_datasource = server.datasources.publish(new_datasource, temp_file_path, TSC.Server.PublishMode.CreateNew)
                        st.success(f"Datasource '{file_name}' uploaded successfully!")
                    
                    elif file_extension in ['tfl', 'tflx']:  # Flow file types
                        # Create a FlowItem to upload
                        new_flow = TSC.FlowItem(name=file_name)
                        new_flow = server.flows.publish(new_flow, temp_file_path, TSC.Server.PublishMode.CreateNew)
                        st.success(f"Flow '{file_name}' uploaded successfully!")

                    else:
                        st.error("Unsupported file type. Please upload a valid Tableau Workbook, Datasource, or Flow file.")

                    # Clean up the temporary file after upload
                    os.remove(temp_file_path)

                # -----------------------------
                # Create Project Section
                st.subheader("Create a New Project")

                # Radio button to choose if the user wants to create a project
                create_project = st.radio("Do you want to create a new project?", ["No", "Yes"])

                if create_project == "Yes":
                    project_name = st.text_input("Enter the name of the new project")
                    project_description = st.text_area("Enter a description for the new project")

                    if st.button("Create Project"):
                        if project_name and project_description:
                            try:
                                # Create a new project in Tableau using TSC
                                new_project = TSC.ProjectItem(
                                    name=project_name,
                                    description=project_description,
                                    content_permissions=None,
                                    parent_id=None,
                                    samples=True
                                )
                                new_project = server.projects.create(new_project)
                                st.success(f"Project '{project_name}' created successfully!")
                            except Exception as e:
                                st.error(f"An error occurred while creating the project: {e}")
                        else:
                            st.error("Please provide both a project name and description.")
                        
        except Exception as e:
            st.error(f"An error occurred while connecting to Tableau: {e}")
    else:
        st.error("Please provide all the necessary credentials.")
