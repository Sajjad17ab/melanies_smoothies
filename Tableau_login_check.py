import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO

# Set up the Tableau connection using secrets
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# Function to convert data to Excel format
def to_excel(users, datasources, workbooks):
    # Create pandas DataFrames
    users_df = pd.DataFrame([user.name for user in users], columns=["User Name"])
    datasources_df = pd.DataFrame([datasource.name for datasource in datasources], columns=["Datasource Name"])
    workbooks_df = pd.DataFrame([workbook.name for workbook in workbooks], columns=["Workbook Name"])

    # Create a BytesIO object to save the Excel file in memory
    output = BytesIO()
    
    # Write to an Excel file in memory
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        users_df.to_excel(writer, sheet_name="Users", index=False)
        datasources_df.to_excel(writer, sheet_name="Datasources", index=False)
        workbooks_df.to_excel(writer, sheet_name="Workbooks", index=False)
    
    # Move to the beginning of the BytesIO object
    output.seek(0)
    return output

# Connect to Tableau Server/Online
try:
    with server.auth.sign_in(tableau_auth):
        # Get the list of users
        all_users, pagination_item = server.users.get()

        # Get the list of datasources
        all_datasources, pagination_item_ds = server.datasources.get()

        # Get the list of workbooks
        all_workbooks_items, pagination_item_wb = server.workbooks.get()

        # Convert data to Excel
        excel_file = to_excel(all_users, all_datasources, all_workbooks_items)
        
        # Provide a download link for the Excel file
        st.download_button(
            label="Download Excel File",
            data=excel_file,
            file_name="tableau_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.write(f"There are {pagination_item.total_available} users, {pagination_item_ds.total_available} datasources, and {pagination_item_wb.total_available} workbooks on the site.")
    
except Exception as e:
    st.error(f"An error occurred while connecting to Tableau: {e}")
