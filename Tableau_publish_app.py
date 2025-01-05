import streamlit as st
import tableauserverclient as TSC
import os

# Title of the Streamlit app
st.title("Publish Tableau Content to Server")

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
