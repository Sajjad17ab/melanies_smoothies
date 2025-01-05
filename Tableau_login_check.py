import streamlit as st
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import get_projects_dataframe

# Streamlit app title
st.title("Tableau Online Login")

# User input fields
username = st.text_input("Username")
password = st.text_input("Password", type="password")
site_id = st.text_input("Site ID (leave blank for default)", '')

# Login button
if st.button("Login"):
    TABLEAU_ONLINE_URL = 'https://prod-apnortheast-a.online.tableau.com'

    # Create a connection object
    connection = TableauServerConnection(
        server=TABLEAU_ONLINE_URL,
        username=username,
        password=password,
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
