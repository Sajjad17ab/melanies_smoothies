import streamlit as st
import requests
import json
import pandas as pd

# Title of the Streamlit app
st.title("Publish or Export Tableau Content to Cloud")

# User input fields for Tableau Authentication (PAT)
st.subheader("Authentication to Tableau")

# Option to choose between Tableau Online (Cloud) and Tableau Server
server_type = st.radio("Select your Tableau type", ("Tableau Online (Cloud)", "Tableau Server"))

# User input for PAT
token_name = st.text_input("Enter your Tableau Personal Access Token (PAT) Name")
token_value = st.text_input("Enter your Tableau Personal Access Token (PAT) Value", type="password")
site = st.text_input("Enter your Tableau Site Name (leave empty for default)", "")

# Input field for Tableau Online URL (only shown if "Tableau Online (Cloud)" is selected)
if server_type == "Tableau Online (Cloud)":
    cloud_url = st.text_input("Enter your Tableau Online Cloud URL (e.g., https://10ay.online.tableau.com)", "")
else:
    cloud_url = ""  # For Tableau Server, no need for this URL

# Server URL setup based on the selected server type
if server_type == "Tableau Online (Cloud)":
    server_url = cloud_url  # Tableau Online Cloud URL provided by the user
else:
    server_url = st.text_input("Enter your Tableau Server URL", "https://your-tableau-server.com")  # Tableau Server URL

# Authentication API URL
auth_url = f"{server_url}/api/3.10/auth/signin"

# Function to login to Tableau Online or Tableau Server
def login_to_tableau():
    payload = {
        "credentials": {
            "name": token_name,
            "password": token_value,
            "site": {
                "contentUrl": site
            }
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make POST request to authenticate
        response = requests.post(auth_url, json=payload, headers=headers)

        # Check for successful login
        if response.status_code == 200:
            st.success("Login successful!")
            response_data = response.json()
            token = response_data["credentials"]["token"]
            site_name = response_data["credentials"]["site"]["contentUrl"]
            user_name = response_data["credentials"]["user"]["name"]
            
            st.write(f"Authenticated User: {user_name}")
            st.write(f"Authenticated Site: {site_name}")
            st.write(f"Authentication Token: {token}")

            return token  # Return token for further API calls

        # If login failed
        else:
            error_message = response.json().get("error", {}).get("detail", "Unknown error")
            st.error(f"Login failed. Status code: {response.status_code}")
            st.write(f"Error Message: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while trying to authenticate: {e}")
        return None


# Button to trigger the login
if st.button("Login to Tableau"):
    # Check if required fields are provided
    if token_name and token_value:
        token = login_to_tableau()
        
        if token:
            # Use the token to get additional info like projects
            if server_type == "Tableau Online (Cloud)":
                # Correct API endpoint for Tableau Online
                projects_url = f"{server_url}/api/3.10/sites/{site}/projects"
            else:
                # Tableau Server - Make sure the correct endpoint URL is provided
                projects_url = f"{server_url}/api/3.10/sites/{site}/projects"
            
            headers = {
                "X-Tableau-Auth": token
            }

            try:
                # Make a GET request to fetch projects
                projects_response = requests.get(projects_url, headers=headers)

                if projects_response.status_code == 200:
                    projects_data = projects_response.json()
                    if 'projects' in projects_data and 'project' in projects_data['projects']:
                        projects = projects_data['projects']['project']
                        if projects:
                            st.write("List of Projects:")
                            for project in projects:
                                st.write(f"Project Name: {project['name']}")
                        else:
                            st.write("No projects found.")
                    else:
                        st.write("The response did not contain project data.")
                else:
                    st.error(f"Failed to fetch projects. Status code: {projects_response.status_code}")
                    st.write(f"Response Text: {projects_response.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred while fetching projects: {e}")
    else:
        st.error("Please enter both the PAT Name and PAT Value.")

# Switch between Upload and Download options after login
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
                    tableau_auth = token  # Directly using the auth token obtained earlier

                    # Create server object and authenticate
                    server = TSC.Server(server_url, use_server_version=True)

                    # Authenticate
                    with server.auth.sign_in(tableau_auth, site=site):  # Passing 'site' here
                        # Find the project by name
                        all_projects, pagination_item = server.projects.get()
                        project = next((proj for proj in all_projects if proj.name == project_name), None)

                        if project is None:
                            st.error(f"Project '{project_name}' not found on the cloud.")
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
                                st.error("Unsupported file type. Please upload a .twbx, .tds, .tdsx, .tfl, or .tfreed file.")

                            # Clean up the temporary file
                            os.remove(temp_file_path)

                except Exception as e:
                    st.error(f"An error occurred during the upload: {e}")

# Download functionality
elif mode == "Download":
    st.subheader("Export All Content Names and Owners to CSV")

    # Export all content with owner to CSV
    if st.button("Export All Content Names and Owners to CSV"):
        try:
            # Authenticate with Tableau again using the token
            headers = {"X-Tableau-Auth": token}
            
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
