import streamlit as st
import tableauserverclient as TSC
import pandas as pd

# Function to sign in to Tableau Server using PAT (Personal Access Token)
def sign_in(token_name: str, token_value: str, tableau_site: str) -> TSC.Server:
    """Sign in to Tableau Server using Personal Access Token.

    Args:
        token_name (str): The name of the Personal Access Token.
        token_value (str): The value of the Personal Access Token.
        tableau_site (str): The site ID for Tableau.

    Returns:
        TSC.Server: The authenticated Tableau Server object or None if failed.
    """
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, tableau_site)
    server = TSC.Server('https://prod-apnortheast-a.online.tableau.com/#/site/mohdsajjadsheikh-8334074aaa/home')

    try:
        server.auth.sign_in(tableau_auth)
        return server
    except Exception as e:
        st.error(f"Failed to sign in: {e}")
        return None

# Function to get workbook connections information
def get_workbooks_connections(server, project_name=None, workbook_name=None) -> pd.DataFrame:
    """Get workbook connection details from Tableau Server.

    Args:
        server (TSC.Server): The authenticated Tableau Server object.
        project_name (str, optional): Filter for specific project name.
        workbook_name (str, optional): Filter for specific workbook name.

    Returns:
        pd.DataFrame: DataFrame containing workbook connection details.
    """
    if not server:
        st.error("Server connection is not established.")
        return pd.DataFrame()

    # Retrieve all workbooks from the server
    all_workbooks = list(TSC.Pager(server.workbooks))
    
    # Filter the list of workbooks based on project_name and workbook_name
    workbooks = list(filter(lambda workbook: (
        (workbook.project_name == project_name or not project_name) and 
        (workbook.name == workbook_name or not workbook_name)
    ), all_workbooks))

    # Extract workbook connection details
    list_of_workbooks = []
    for workbook in workbooks:
        server.workbooks.populate_connections(workbook)  # Populate connections for the workbook
        for connection in workbook.connections:
            list_of_workbooks.append([
                workbook.project_name, 
                workbook.name, 
                connection.datasource_name, 
                connection.connection_type, 
                connection.username
            ])

    # Create a Pandas DataFrame
    data = pd.DataFrame(list_of_workbooks, columns=['project_name', 'workbook_name', 'datasource_name', 'connection_type', 'connection_username'])

    return data

# Streamlit app layout
st.title("Tableau Server Workbook Connections")

# User inputs
token_name = st.text_input("Enter your Personal Access Token Name:")
token_value = st.text_input("Enter your Personal Access Token Value:", type="password")
site_id = st.text_input("Enter your Tableau Site ID (leave blank for default):")
project_name = st.text_input("Enter Project Name (optional):")
workbook_name = st.text_input("Enter Workbook Name (optional):")

# Login button
if st.button("Login and Get Workbook Connections"):
    server = sign_in(token_name, token_value, site_id or '')
    
    if server:
        connections_df = get_workbooks_connections(server, project_name, workbook_name)
        if not connections_df.empty:
            st.success("Successfully retrieved workbook connections!")
            st.dataframe(connections_df)
        else:
            st.warning("No workbook connections found.")
