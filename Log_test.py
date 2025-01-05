import streamlit as st
import tableauserverclient as TSC

# Function to authenticate and list workbooks
def get_tableau_workbooks(server_url, username, pat_name, pat_secret, site_id=''):
    # Authenticate with Tableau Cloud using PAT
    tableau_auth = TSC.PersonalAccessTokenAuth(pat_name, pat_secret, site=site_id)
    server = TSC.Server(server_url, use_server_version=True)

    try:
        # Sign in to Tableau Cloud
        with server.auth.sign_in(tableau_auth):
            # Fetch workbooks
            all_workbooks, pagination_item = server.workbooks.get()
            workbooks_list = [workbook.name for workbook in all_workbooks]
            return workbooks_list
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
def main():
    st.title("Tableau Cloud Connection")

    # Input fields for user credentials and information
    server_url = st.text_input("Enter Tableau Cloud URL (e.g., https://10ax.online.tableau.com):")
    username = st.text_input("Enter your Tableau username:")
    pat_name = st.text_input("Enter your Personal Access Token name:")
    pat_secret = st.text_input("Enter your Personal Access Token secret:", type="password")
    site_id = st.text_input("Enter Site ID (Leave empty for default site):")
    
    # Button to fetch workbooks
    if st.button("Fetch Workbooks"):
        if server_url and username and pat_name and pat_secret:
            workbooks = get_tableau_workbooks(server_url, username, pat_name, pat_secret, site_id)
            if isinstance(workbooks, list):
                if workbooks:
                    st.subheader("List of Workbooks in your Tableau Cloud:")
                    for workbook in workbooks:
                        st.write(f"- {workbook}")
                else:
                    st.write("No workbooks found.")
            else:
                st.error(workbooks)  # Display error message if an exception occurred
        else:
            st.error("Please fill in all required fields.")

# Run the app
if __name__ == "__main__":
    main()
