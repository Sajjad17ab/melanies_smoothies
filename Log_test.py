import streamlit as st
import tableauserverclient as TSC

# Function to sign in to Tableau Cloud and get server information
def login_to_tableau(username, token, site_name=""):
    try:
        # Set the server URL for Tableau Cloud (modify for your region if needed)
        server_url = "https://10ax.online.tableau.com"  # Modify as needed
        
        # Create a Tableau Server Client instance
        server = TSC.Server(server_url)
        
        # Set up Tableau authentication using the provided credentials
        tableau_auth = TSC.TableauAuth(username, token, site=site_name)
        
        # Sign in to Tableau Cloud
        with server.auth.sign_in(tableau_auth):
            server_info = server.server_info
            return f"Successfully logged in to Tableau Cloud at: {server_info.baseurl}", server_info
    except Exception as e:
        return f"Error: {e}", None

# Streamlit interface
def main():
    # Title and description
    st.title("Tableau Cloud Login")
    st.write("Enter your Tableau Cloud credentials (email and PAT) to log in and view server information.")
    
    # User input for credentials (email and PAT token for login)
    username = st.text_input("Email (Username)", "")
    token = st.text_input("Personal Access Token", type="password")
    site_name = st.text_input("Site Name (Leave empty for default)", "")

    # Button to attempt login
    if st.button("Login"):
        if username and token:
            st.write("Attempting to log in...")
            result, server_info = login_to_tableau(username, token, site_name)
            
            # Display result
            if "Error" in result:
                st.error(result)  # Show error message if login fails
            else:
                st.success(result)  # Show success message if login succeeds
                st.write("Server Information:")
                st.json(server_info.__dict__)  # Display the server info as JSON
                
        else:
            st.warning("Please enter both email and PAT token.")  # Show a warning if credentials are missing

# Run the app
if __name__ == "__main__":
    main()
