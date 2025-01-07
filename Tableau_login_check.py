import streamlit as st
import tableauserverclient as TSC
import pandas as pd

# Set up the Tableau connection using secrets
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# Connect to Tableau Server/Online
try:
    with server.auth.sign_in(tableau_auth):
        # Get the list of users
        all_users, pagination_item = server.users.get()
        st.write(f"There are {pagination_item.total_available} users on the site:")
        
        # Convert user names to a pandas DataFrame
        users_df = pd.DataFrame([user.name for user in all_users], columns=["User Name"])
        st.dataframe(users_df)  # Display the users in a table format

        # Get the list of datasources
        all_datasources, pagination_item_ds = server.datasources.get()
        st.write(f"\nThere are {pagination_item_ds.total_available} datasources on the site:")

        # Convert datasource names to a pandas DataFrame
        datasources_df = pd.DataFrame([datasource.name for datasource in all_datasources], columns=["Datasource Name"])
        st.dataframe(datasources_df)  # Display the datasources in a table format
        
        # Get the list of workbooks
        all_workbooks_items, pagination_item_wb = server.workbooks.get()
        st.write(f"\nThere are {pagination_item_wb.total_available} workbooks on the site:")

        # Convert workbook names to a pandas DataFrame
        workbooks_df = pd.DataFrame([workbook.name for workbook in all_workbooks_items], columns=["Workbook Name"])
        st.dataframe(workbooks_df)  # Display the workbooks in a table format

except Exception as e:
    st.error(f"An error occurred while connecting to Tableau: {e}")
