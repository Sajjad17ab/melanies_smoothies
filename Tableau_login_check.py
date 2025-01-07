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

        # Get the list of datasources
        all_datasources, pagination_item_ds = server.datasources.get()

        # Get the list of workbooks
        all_workbooks_items, pagination_item_wb = server.workbooks.get()

        # Combine all the data into one DataFrame
        users_df = pd.DataFrame([user.name for user in all_users], columns=["Name"])
        users_df["Type"] = "User"

        datasources_df = pd.DataFrame([datasource.name for datasource in all_datasources], columns=["Name"])
        datasources_df["Type"] = "Datasource"

        workbooks_df = pd.DataFrame([workbook.name for workbook in all_workbooks_items], columns=["Name"])
        workbooks_df["Type"] = "Workbook"

        # Concatenate all data into one DataFrame
        combined_df = pd.concat([users_df, datasources_df, workbooks_df], ignore_index=True)

        # Display the combined DataFrame in a table format
        st.write(f"There are {combined_df.shape[0]} total entries:")
        st.dataframe(combined_df)  # Display the combined table

except Exception as e:
    st.error(f"An error occurred while connecting to Tableau: {e}")
