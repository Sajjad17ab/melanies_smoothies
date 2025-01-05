import streamlit as st
import tableauserverclient as TSC
import os

# Title of the Streamlit app
st.title("Publish Tableau Workbook, Data Source, and Flow to Server")

# User inputs for authentication
st.subheader("Authentication")
token_name = st.text_input("Enter your Personal Access Token (PAT) name", "")
token_value = st.text_input("Enter your Personal Access Token (PAT) value", "")
server_url = st.text_input("Enter your Tableau server URL", "https://your-tableau-server.com")
site = st.text_input("Enter your site name (leave empty for default)", "")

# User input for project details
project_name = st.text_input("Enter the project name on Tableau Server", "your_project")

# File uploader for Tableau files
uploaded_file_workbook = st.file_uploader("Upload your Tableau workbook (.twbx)", type=["twbx"])
uploaded_file_data_source = st.file_uploader("Upload your Tableau data source (.tds, .tdsx)", type=["tds", "tdsx"])
uploaded_file_flow = st.file_uploader("Upload your Tableau flow (.tfl, .tfreed)", type=["tfl", "tfreed"])

if uploaded_file_workbook or uploaded_file_data_source or uploaded_file_flow:
    st.write("File(s) uploaded successfully!")

    # When the user clicks 'Publish'
    if st.button("Publish to Tableau Server"):
        if not token_name or not token_value or not server_url or not project_name:
            st.error("Please fill in all the required fields before publishing.")
        else:
            try:
                # Create authentication object
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
                        # Publishing a Workbook
                        if uploaded_file_workbook:
                            workbook_item = TSC.WorkbookItem(project.id)
                            with open("temp_workbook.twbx", "wb") as f:
                                f.write(uploaded_file_workbook.getbuffer())
                            new_workbook = server.workbooks.publish(workbook_item, "temp_workbook.twbx", TSC.PublishMode.CreateNew)
                            st.success(f"Workbook '{new_workbook.name}' has been successfully published.")

                            # Clean up the temporary workbook file
                            os.remove("temp_workbook.twbx")
                        
                        # Publishing a Data Source
                        if uploaded_file_data_source:
                            data_source_item = TSC.DatasourceItem(project.id)
                            with open("temp_data_source.tds", "wb") as f:
                                f.write(uploaded_file_data_source.getbuffer())
                            new_data_source = server.datasources.publish(data_source_item, "temp_data_source.tds", TSC.PublishMode.CreateNew)
                            st.success(f"Data source '{new_data_source.name}' has been successfully published.")

                            # Clean up the temporary data source file
                            os.remove("temp_data_source.tds")

                        # Publishing a Flow
                        if uploaded_file_flow:
                            flow_item = TSC.FlowItem(project.id)
                            with open("temp_flow.tfl", "wb") as f:
                                f.write(uploaded_file_flow.getbuffer())
                            new_flow = server.flows.publish(flow_item, "temp_flow.tfl", TSC.PublishMode.CreateNew)
                            st.success(f"Flow '{new_flow.name}' has been successfully published.")

                            # Clean up the temporary flow file
                            os.remove("temp_flow.tfl")

            except Exception as e:
                st.error(f"An error occurred: {e}")
