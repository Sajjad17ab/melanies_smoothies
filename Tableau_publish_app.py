import streamlit as st
import tableauserverclient as TSC
import os
import pandas as pd

# Title of the Streamlit app
st.title("Publish, Export or Onboard Tableau Content/Users to Server")

# Mode selection - Switch between Upload, Download, and Onboard Users
mode = st.radio("Choose an option", ("Upload", "Download", "Onboard Users"))

# Authentication method selection (radio button)
auth_method = st.radio("Select Authentication Method", ("Username/Password", "Personal Access Token (PAT)"))

# Authentication input fields (conditional based on selected method)
if auth_method == "Username/Password":
    st.subheader("Username and Password Authentication")
    username = st.text_input("Enter your Tableau username", "")
    password = st.text_input("Enter your Tableau password", "", type="password")
else:
    st.subheader("Personal Access Token (PAT) Authentication")
    token_name = st.text_input("Enter your Personal Access Token (PAT) name", "")
    token_value = st.text_input("Enter your Personal Access Token (PAT) value", "")

server_url = st.text_input("Enter your Tableau server URL", "https://your-tableau-server.com")
site = st.text_input("Enter your site name (leave empty for default)", "")

# Switch between Upload, Download, and Onboard Users
if mode == "Upload":
    st.subheader("Upload Tableau Content to Server")

    # User input for project details
    project_name = st.text_input("Enter the project name on Tableau Server", "your_project")

    # Single file uploader (accepts multiple types)
    uploaded_file = st.file_uploader("Upload your Tableau file (.twbx, .tds, .tdsx, .tfl, .tfreed)", 
                                     type=["twbx", "tds", "tdsx", "tfl", "tfreed"])

    if uploaded_file:
        st.write("File uploaded successfully!")

        # When the user clicks 'Publish'
        if st.button("Publish to Tableau Server"):
            if not server_url or not project_name:
                st.error("Please fill in all the required fields before publishing.")
            else:
                try:
                    # Create authentication object based on selected method
                    if auth_method == "Username/Password":
                        if not username or not password:
                            st.error("Please provide both username and password.")
                        else:
                            tableau_auth = TSC.TableauAuth(username, password, site=site)
                    else:
                        if not token_name or not token_value:
                            st.error("Please provide both token name and token value.")
                        else:
                            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)

                    # Create server object and authenticate
                    server = TSC.Server(server_url, use_server_version=True)

                    # Authenticate
                    with server.auth.sign_in(tableau_auth):
                        # Find the project by name
                        all_projects, pagination_item = server.projects.get()
                        project = next((proj for proj in all_projects if proj.name == project_name), None)

                        if project is None:
                            st.error(f"Project '{project_name}' not found on the server.")
                        else:
                            # Save the uploaded file to a temporary location
                            temp_file_path = "temp_uploaded_file"
                            with open(temp_file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            # Determine file type based on extension
                            file_extension = uploaded_file.name.split('.')[-1].lower()

                            if file_extension == "twbx":
                                # Publishing a Workbook
                                workbook_item = TSC.WorkbookItem(project.id)
                                new_workbook = server.workbooks.publish(workbook_item, temp_file_path, TSC.PublishMode.CreateNew)
                                st.success(f"Workbook '{new_workbook.name}' has been successfully published.")
                                
                            elif file_extension in ["tds", "tdsx"]:
                                # Publishing a Data Source
                                data_source_item = TSC.DatasourceItem(project.id)
                                new_data_source = server.datasources.publish(data_source_item, temp_file_path, TSC.PublishMode.CreateNew)
                                st.success(f"Data source '{new_data_source.name}' has been successfully published.")
                                
                            elif file_extension in ["tfl", "tfreed"]:
                                # Publishing a Flow
                                flow_item = TSC.FlowItem(project.id)
                                new_flow = server.flows.publish(flow_item, temp_file_path, TSC.PublishMode.CreateNew)
                                st.success(f"Flow '{new_flow.name}' has been successfully published.")

                            else:
                                st.error("Unsupported file type.")

                            # Clean up the temporary file
                            os.remove(temp_file_path)

                except Exception as e:
                    st.error(f"An error occurred: {e}")

elif mode == "Download":
    st.subheader("Export All Content Names and Owners to CSV")

    # Export all content with owner to CSV
    if st.button("Export All Content Names and Owners to CSV"):
        try:
            if not server_url:
                st.error("Please enter the Tableau server URL first.")
            elif not project_name:
                st.error("Please enter the project name.")
            else:
                # Authenticate again if needed
                if auth_method == "Username/Password":
                    if not username or not password:
                        st.error("Please provide both username and password.")
                    else:
                        tableau_auth = TSC.TableauAuth(username, password, site=site)
                else:
                    if not token_name or not token_value:
                        st.error("Please provide both token name and token value.")
                    else:
                        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)

                # Authenticate with Tableau Server
                with server.auth.sign_in(tableau_auth):
                    # Collect all workbooks, data sources, and flows
                    content_data = []

                    # Get Workbooks
                    all_workbooks, _ = server.workbooks.get()
                    for workbook in all_workbooks:
                        content_data.append({"Content Type": "Workbook", "Name": workbook.name, "Owner": workbook.owner.name})

                    # Get Data Sources
                    all_data_sources, _ = server.datasources.get()
                    for data_source in all_data_sources:
                        content_data.append({"Content Type": "Data Source", "Name": data_source.name, "Owner": data_source.owner.name})

                    # Get Flows
                    all_flows, _ = server.flows.get()
                    for flow in all_flows:
                        content_data.append({"Content Type": "Flow", "Name": flow.name, "Owner": flow.owner.name})

                    # Convert to DataFrame
                    df = pd.DataFrame(content_data)

                    # Export to CSV (downloadable)
                    csv = df.to_csv(index=False)
                    st.download_button("Download CSV", csv, "content_and_owners.csv", "text/csv")

        except Exception as e:
            st.error(f"An error occurred while exporting: {e}")

elif mode == "Onboard Users":
    st.subheader("Onboard Users from CSV to Tableau Server")

    # Upload CSV for onboarding users
    uploaded_csv = st.file_uploader("Upload a CSV file with user details (username, email, role)", type=["csv"])

    if uploaded_csv:
        st.write("CSV uploaded successfully!")

        # When the user clicks 'Onboard Users'
        if st.button("Onboard Users to Tableau Server"):
            if not server_url:
                st.error("Please enter the Tableau server URL.")
            else:
                try:
                    # Read the CSV and onboard users
                    user_data = pd.read_csv(uploaded_csv)

                    if "username" not in user_data.columns or "email" not in user_data.columns or "role" not in user_data.columns:
                        st.error("CSV must contain 'username', 'email', and 'role' columns.")
                    else:
                        # Authenticate again if needed
                        if auth_method == "Username/Password":
                            if not username or not password:
                                st.error("Please provide both username and password.")
                            else:
                                tableau_auth = TSC.TableauAuth(username, password, site=site)
                        else:
                            if not token_name or not token_value:
                                st.error("Please provide both token name and token value.")
                            else:
                                tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)

                        # Authenticate with Tableau Server
                        with server.auth.sign_in(tableau_auth):
                            # Onboard each user
                            for _, row in user_data.iterrows():
                                try:
                                    user = TSC.UserItem(row['username'], row['role'], row['email'])
                                    server.users.add(user)
                                    st.success(f"User {row['username']} onboarded successfully.")
                                except Exception as e:
                                    st.error(f"Failed to onboard {row['username']}: {e}")

                except Exception as e:
                    st.error(f"An error occurred while onboarding users: {e}")
