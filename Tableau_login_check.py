import streamlit as st
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import get_projects_dataframe

# Streamlit app title
st.title("Tableau Cloud Login")

# User input fields
tableau_url = st.text_input("Tableau Cloud URL", value='https://prod-apnortheast-a.online.tableau.com')

# Authentication method selection
auth_method = st.radio("Choose Authentication Method", ("Username and Password", "Personal Access Token (PAT)"))

if auth_method == "Username and Password":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    pat_name = ""
    pat_value = ""
elif auth_method == "Personal Access Token (PAT)":
    username = ""
    password = ""
    pat_name = st.text_input("Personal Access Token Name")
    pat_value = st.text_input("Personal Access Token Value", type="password")

site_id = st.text_input("Site ID (leave blank for default)", '')

# Login button
if st.button("Login"):
    try:
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
    except Exception as e:
        st.error(f"An error occurred: {e}")
