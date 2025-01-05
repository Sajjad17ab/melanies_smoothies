import streamlit as st
import tableauserverclient as TSC

# Title of the Streamlit app
st.title("Publish Tableau Workbook")

# Switch between Tableau Cloud and Tableau Server
connection_type = st.radio("Select Connection Type", ("Tableau Cloud", "Tableau Server"))

# User inputs for authentication
st.subheader("Authentication")
token_name = st.text_input("Enter your Personal Access Token (PAT) name", "")
token_value = st.text_input("Enter your Personal Access Token (PAT) value", "")

# Server URL input based on connection type
if connection_type == "Tableau Server":
    server_url = st.text_input("Enter your Tableau Server URL", "https://your-tableau-server.com")
else:
    cloud_url = st.text_input("Enter your Tableau Cloud URL", "https://your-site.online.tableau.com")  # Tableau Cloud URL

site = st.text_input("Enter your site name (leave empty for default)", "")

# User input for project details
project_name = st.text_input("Enter the project name on Tableau Server/Cloud", "your_project")

# File uploader for the Tableau workbook
uploaded_file = st.file_uploader("Upload your Tableau workbook (.twbx)", type=["twbx"])

if uploaded_file:
    st.write("File uploaded successfully!")

    # When the user clicks 'Publish'
    if st.button("Publish Workbook"):
        if not token_name or not token_value or (not server_url and not cloud_url) or not project_name:
            st.error("Please fill in all the required fields before publishing.")
        else:
            try:
                # Create authentication object
                if connection_type == "Tableau Server":
                    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)
                    server = TSC.Server(server_url, use_server_version=True)
                else:
                    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)
                    server = TSC.Server(cloud_url, use_server_version=True)

                # Authenticate
                with server.auth.sign_in(tableau_auth):
                    # Find the project by name
                    all_projects, pagination_item = server.projects.get()
                    project = next((proj for proj in all_projects if proj.name == project_name), None)

                    if project is None:
                        st.error(f"Project '{project_name}' not found on the server.")
                    else:
                        # Publish the workbook
                        workbook_item = TSC.WorkbookItem(project.id)
                        # Save the uploaded workbook to a temporary file location
                        with open("temp_workbook.twbx", "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        new_workbook = server.workbooks.publish(workbook_item, "temp_workbook.twbx", TSC.PublishMode.CreateNew)
                        
                        # Provide success feedback
                        st.success(f"Workbook '{new_workbook.name}' has been successfully published to the '{project_name}' project.")

                        # Clean up the temporary file
                        import os
                        os.remove("temp_workbook.twbx")

            except Exception as e:
                st.error(f"An error occurred: {e}")
