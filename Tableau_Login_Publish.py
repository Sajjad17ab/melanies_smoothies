import tableauserverclient as TSC

# Define connection parameters
server_url = 'https://your-tableau-server.com'  # Tableau server URL
site = ''  # Default site is empty; specify the site name if you're using one

# Option 1: Authentication using username and password
# Uncomment the next 3 lines and comment out the PAT section to use username/password authentication
username = 'your_username'  # Your Tableau username
password = 'your_password'  # Your Tableau password
# tableau_auth = TSC.TableauAuth(username, password, site=site)

# Option 2: Authentication using Personal Access Token (PAT)
# Uncomment the next 3 lines and comment out the username/password section to use PAT
token_name = 'your_token_name'  # The name of your personal access token
token_value = 'your_token_value'  # The value of your personal access token
tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site=site)

# Path to the local Tableau workbook
file_path = 'path_to_your_local_workbook.twbx'  # Replace with the path to your local workbook

# Define the project on Tableau Server where the workbook will be published
project_name = 'your_project'  # Replace with the project name where you want to publish the workbook

# Create a server object and authenticate
server = TSC.Server(server_url, use_server_version=True)

# Publish the workbook to Tableau Server
with server.auth.sign_in(tableau_auth):
    # Find the project by name
    all_projects, pagination_item = server.projects.get()
    project = next((proj for proj in all_projects if proj.name == project_name), None)

    if project is None:
        raise ValueError(f"Project '{project_name}' not found on the server.")

    # Publish the workbook
    workbook = TSC.WorkbookItem(project.id)
    new_workbook = server.workbooks.publish(workbook, file_path, TSC.Server.PublishMode.CreateNew)
    
    print(f"Workbook '{new_workbook.name}' has been successfully published.")
