import tableauserverclient as TSC

def main():
    # This is the domain for Tableau's Developer Program (replace with your Tableau Cloud URL)
    server_url = "https://sso.online.tableau.com/public/login"  # Modify the server URL if needed for your region
    
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
import streamlit as st
import tableauserverclient as TSC

# Function to sign in and get server information
def login_to_tableau(username, password, site_name=""):
    try:
        # Set the server URL for Tableau Cloud (replace with your region if needed)
        server_url = "https://prod-apnortheast-a.online.tableau.com/#/site/mohdsajjadsheikh-8334074aaa/home"
        
        # Create the Tableau Server Client instance
        server = TSC.Server(server_url)
        
        # Create authentication credentials
        tableau_auth = TSC.TableauAuth(username, password, site=site_name)
        
        # Sign in to the server
        with server.auth.sign_in(tableau_auth):
            server_info = server.server_info
            return f"Successfully logged in to Tableau Cloud at: {server_info.baseurl}", server_info
    except Exception as e:
        return f"Error: {e}", None

# Streamlit interface
def main():
    st.title("Tableau Cloud Login")
    st.write("Enter your Tableau Cloud credentials to log in.")

    # User inputs for credentials
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    site_name = st.text_input("Site Name (Leave empty for default)")

    # Button to initiate login
    if st.button("Login"):
        if username and password:
            st.write("Attempting to log in...")
            result, server_info = login_to_tableau(username, password, site_name)

            if "Error" in result:
                st.error(result)
            else:
                st.success(result)
                st.write("Server Information:")
                st.json(server_info.__dict__)  # Display the server info in JSON format
        else:
            st.warning("Please enter both username and password.")

# Run the app
if __name__ == "__main__":
    main()
