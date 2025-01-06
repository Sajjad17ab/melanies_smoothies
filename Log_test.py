import tableauserverclient as TSC

def main():
    # This is the domain for Tableau's Developer Program (replace with your Tableau Cloud URL)
    server_url = "https://10ax.online.tableau.com"  # Modify the server URL if needed for your region
    
    # Tableau credentials (replace with your actual username, password, and site name)
    username = "your_username"  # Replace with your Tableau username
    password = "your_password"  # Replace with your Tableau password
    site_name = ""  # Leave empty for the default site or replace with your specific site name
    
    # Create a Tableau Server Client instance
    server = TSC.Server(server_url)
    
    # Authentication
    tableau_auth = TSC.TableauAuth(username, password, site=site_name)
    
    # Sign in to Tableau Cloud and fetch server information
    try:
        with server.auth.sign_in(tableau_auth):
            print(f"Successfully signed in to Tableau Server at: {server.server_info.baseurl}")
            print("Server information:")
            print(f"  - Version: {server.server_info.version}")
            print(f"  - Server Info: {server.server_info}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
