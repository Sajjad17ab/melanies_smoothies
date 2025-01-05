import streamlit as st
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import get_projects_dataframe

# Streamlit app title
st.title("Tableau Online Login")

# User input fields
tableau_url = st.text_input("Tableau Cloud URL", value='https://prod-apnortheast-a.online.tableau.com')
username = st.text_input("Username (leave blank if using PAT)", "")
password = st.text_input("Password (leave blank if using PAT)", type="password")
pat_name = st.text_input("Personal Access Token Name (leave blank if using Username/Password)", "")
pat_value = st.text_input("Personal Access Token Value (leave blank if using Username/Password)", type="password")
site_id = st.text_input("Site ID (leave blank for default)", '')

# Login button
if st.button("Login"):
    if (username and password) and (pat_name or pat_value):
        st.error("Please provide either Username/Password OR Personal Access Token, not both.")
    else:
        # Create a connection object based on provided credentials
        connection = TableauServerConnection(
            server=tableau_url,
            username=username if username else None,
            password=password if password else None,
            personal_access_token_name=pat_name if pat_name else None,
            personal_access_token_value=pat_value if pat_value else None,
            site_id=site_id
        )

        # Log in to Tableau Online
        connection.sign_in()

        # Check if login was successful
        if connection.is_signed_in():
            st.success("Successfully logged in to Tableau Online!")

            # Example: Get a list of projects
            projects_df = get_projects_dataframe(connection)
            st.write("Projects:", projects_df)

            # Sign out when done
            connection.sign_out()
        else:
            st.error("Login failed. Please check your credentials.")
