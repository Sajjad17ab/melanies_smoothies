import csv
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

# Create a server object and authenticate
server = TSC.Server(server_url, use_server_version=True)

# Function to export dashboard, data source, and user information to CSV
def export_dashboard_data_to_csv(csv_file_path):
    # Open CSV file for writing
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Dashboard Name', 'Data Source Name', 'User Name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header to CSV
        writer.writeheader()

        with server.auth.sign_in(tableau_auth):
            # Get all workbooks (dashboards) from Tableau Server
            all_workbooks, pagination_item = server.workbooks.get()
            
            for workbook in all_workbooks:
                # Get datasources for the workbook
                datasources, _ = server.workbooks.populate_connections(workbook)

                # Get all users on Tableau Server
                users, _ = server.users.get()

                # Write the dashboard, data source, and user information
                for datasource in datasources:
                    for user in users:
                        # Write a row for each combination of dashboard, data source, and user
                        writer.writerow({
                            'Dashboard Name': workbook.name,
                            'Data Source Name': datasource.name,
                            'User Name': user.name
                        })
                        print(f"Writing: {workbook.name}, {datasource.name}, {user.name}")

    print(f"Export complete! Data saved to {csv_file_path}")

# Define path to save the CSV file
csv_file_path = 'tableau_export.csv'  # Replace with your desired CSV file path

# Call the function to export data
export_dashboard_data_to_csv(csv_file_path)
