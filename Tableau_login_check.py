import streamlit as st
import tableauserverclient as TSC
import pandas as pd
import io

# Set up the Tableau connection using secrets
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# Function to create the Excel file in-memory
def create_excel(df):
    # Create a BytesIO object to store the Excel file in-memory
    excel_buffer = io.BytesIO()
    
    # Write the dataframe to the in-memory Excel file
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tableau Data')
    
    excel_buffer.seek(0)  # Reset buffer pointer to the beginning
    return excel_buffer

# Connect to Tableau Server/Online
try:
    with server.auth.sign_in(tableau_auth):
        # Get the list of users
        all_users, pagination_item = server.users.get()

        # Get the list of datasources
        all_datasources, pagination_item_ds = server.datasources.get()

        # Get the list of workbooks
        all_workbooks_items, pagination_item_wb = server.workbooks.get()

        # Combine all the data into one DataFrame for users
        users_df = pd.DataFrame([(user.id, user.name, user.name) for user in all_users], columns=["ID", "Name", "Owner"])
        users_df["Type"] = "User"

        # Combine all the data into one DataFrame for datasources
        datasources_df = pd.DataFrame(
            [(datasource.id, datasource.name, datasource.created_by.name if datasource.created_by else "Unknown") for datasource in all_datasources],
            columns=["ID", "Name", "Owner"]
        )
        datasources_df["Type"] = "Datasource"

        # Combine all the data into one DataFrame for workbooks
        workbooks_df = pd.DataFrame(
            [(workbook.id, workbook.name, workbook.owner.name) for workbook in all_workbooks_items],
            columns=["ID", "Name", "Owner"]
        )
        workbooks_df["Type"] = "Workbook"

        # Concatenate all data into one DataFrame
        combined_df = pd.concat([users_df, datasources_df, workbooks_df], ignore_index=True)

        # Display the combined DataFrame in a table format
        st.write(f"There are {combined_df.shape[0]} total entries:")
        st.dataframe(combined_df)  # Display the combined table

        # Create the Excel file from the dataframe
        excel_file = create_excel(combined_df)

        # Provide a download button for the Excel file
        st.download_button(
            label="Download Excel file",
            data=excel_file,
            file_name="tableau_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"An error occurred while connecting to Tableau: {e}")
