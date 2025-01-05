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

# CSV file path containing user data (update this with your actual local file path)
csv_file_path = r'C:/Users/YourUsername/Documents/users.csv'  # Replace with the path to your local CSV file
# On a Mac or Linux machine, the path might look like: '/Users/YourUsername/Documents/users.csv'

# Create a server object and authenticate
server = TSC.Server(server_url, use_server_version=True)

# Function to onboard users from CSV to Tableau Server
def onboard_users_from_csv(csv_file_path):
    # Read the CSV file containing user data
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        with server.auth.sign_in(tableau_auth):
            for row in csv_reader:
                username = row['username']
                email = row['email']
                role = row['role']
                
                # Create user
                try:
                    # Check if the role is valid (Viewer, Explorer, Creator, etc.)
                    if role not in ['Viewer', 'Explorer', 'Creator']:
                        print(f"Invalid role '{role}' for user {username}. Skipping...")
                        continue
                    
                    user = TSC.UserItem(username, email, site_role=role)
                    created_user = server.users.create(user)
                    
                    print(f"User '{created_user.name}' onboarded successfully!")
                except Exception as e:
                    print(f"Error onboarding user '{username}': {e}")

# Call the function to onboard users from CSV
onboard_users_from_csv(csv_file_path)
