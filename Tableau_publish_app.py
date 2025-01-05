import streamlit as st
import tableauserverclient as TSC
import os
import pandas as pd
import uuid

# Title of the Streamlit app
st.title("Publish or Export Tableau Content to Cloud")

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

# Tableau Cloud URL and Site
server_url = st.text_input("Enter your Tableau Cloud URL", "https://your-tableau-cloud.com")
site = st.text_input("Enter your site name (leave empty for default)", "")

# Switch between Upload and Download options
mode = st.radio("Choose an option", ("Upload", "Download"))

# Upload functionality
if mode == "Upload":
    st.subheader("Upload Tableau Content to Cloud")

    # User input for project details
    project_name = st.text_input("Enter the project name on Tableau Cloud", "your_project")

    # Single file uploader (accepts multiple types)
    uploaded_file = st.file_uploader("Upload your Tableau file (.twbx, .tds, .tdsx, .tfl, .tfreed)", 
                                     type=["twbx", "tds", "tdsx", "tfl", "tfreed"])

    if uploaded_file:
        st.write("File uploaded successfully!")

        # When the user clicks 'Publish'
        if st.button("Publish to Tableau Cloud"):
            if not server_url or not project_name:
                st.error("Please fill in all the required fields before publishing.")
            else:
                try:
                    # Create authentication object based on selected method
                    if auth_method == "Username/Password":
                        if not username or not password:
                            st.error("Please provide both username and password.")
                        else:
                            tableau_auth = TSC.TableauAuth(username, password)
                    else:
                        if not token_name or not token_value:
                            st.error("Please provide both token name and token value.")
                        else:
                            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value)

                    # Create server object and authenticate
                    server = TSC.Server(server_url, use_server_version=True)

                    # Authenticate
                    with server.auth.sign_in(tableau_auth, site=site):  # Passing 'site' here
                        # Verification: Fetch a list of projects to check the connection
                        all_projects, _ = server.projects.get()
                        
                        if all_projects:
                            st.success("Successfully connected to Tableau Cloud!")
                        else:
                            st.error("Connection to Tableau Cloud failed. No projects found.")

                        # Find the project by name
                        project = next((proj for proj in all_projects if proj.name == project_name), None)

                        if project is None:
                            st.error(f"Project '{project_name}' not found on the cloud.")
                        else:
                            # Save the uploaded file to a temporary location
                            temp_file_name = f"temp_uploaded_file_{uuid.uuid4().hex}"
                            temp_file_path = os.path.join("/tmp", temp_file_name)
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
                                st.error("Unsupported file type. Please upload a .twbx, .tds, .tdsx, .tfl, or .tfreed file.")

                            # Clean up the temporary file
                            os.remove(temp_file_path)

                except Exception as e:
                    st.error(f"An error occurred: {e}")

# Download functionality
elif mode == "Download":
    st.subheader("Export All Content Names and Owners to CSV")

    # Export all content with owner to CSV
    if st.button("Export All Content Names and Owners to CSV"):
        try:
            if not server_url:
                st.error("Please enter the Tableau Cloud URL first.")
            else:
                # Authenticate again if needed
                if auth_method == "Username/Password":
                    if not username or not password:
                        st.error("Please provide both username and password.")
                    else:
                        tableau_auth = TSC.TableauAuth(username, password)
                else:
                    if not token_name or not token_value:
                        st.error("Please provide both token name and token value.")
                    else:
                        tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value)

                # Authenticate with Tableau Cloud
                with server.auth.sign_in(tableau_auth, site=site):  # Passing 'site' here
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
