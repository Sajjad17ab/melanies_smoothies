import streamlit as st
import tableauserverclient as TSC
import pandas as pd
from io import BytesIO

# Streamlit UI for user credentials input
st.title("Tableau Login with Personal Access Token (PAT)")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Button to trigger the connection
if st.button("Connect to Tableau"):
    if token_name and token_value and site_id and server_url:
        try:
            # Tableau authentication using Personal Access Token (PAT)
            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
            server = TSC.Server(server_url, use_server_version=True)

            # Connect to Tableau Server/Online
            with server.auth.sign_in(tableau_auth):
                # Get the list of users
                all_users, pagination_item = server.users.get()

                # Get the list of datasources
                all_datasources, pagination_item_ds = server.datasources.get()

                # Get the list of workbooks
                all_workbooks_items, pagination_item_wb = server.workbooks.get()

                # Combine all the data into one DataFrame for users
                users_df = pd.DataFrame([(user.id, user.name) for user in all_users], columns=["ID", "Name"])
                users_df["Type"] = "User"  # Add a 'Type' column indicating that this data is about users

                # Combine all the data into one DataFrame for datasources
                datasources_df = pd.DataFrame([(datasource.id, datasource.name) for datasource in all_datasources], columns=["ID", "Name"])
                datasources_df["Type"] = "Datasource"  # Add a 'Type' column indicating that this data is about datasources

                # Combine all the data into one DataFrame for workbooks
                workbooks_df = pd.DataFrame([(workbook.id, workbook.name) for workbook in all_workbooks_items], columns=["ID", "Name"])
                workbooks_df["Type"] = "Workbook"  # Add a 'Type' column indicating that this data is about workbooks

                # Concatenate all data into one DataFrame
                combined_df = pd.concat([users_df, datasources_df, workbooks_df], ignore_index=True)

                # Display the combined DataFrame in a table format
                st.write(f"There are {combined_df.shape[0]} total entries:")
                st.dataframe(combined_df)  # Display the combined table in Streamlit app

                # Convert the DataFrame to an Excel file
                def to_excel(df):
                    # Create a BytesIO object and write the DataFrame to it as an Excel file
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Tableau Data")
                    output.seek(0)  # Rewind the buffer to the beginning
                    return output

                # Prepare the Excel file for download
                excel_file = to_excel(combined_df)

                # Add a download button to allow the user to download the file
                st.download_button(
                    label="Download Excel file",
                    data=excel_file,
                    file_name="tableau_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"An error occurred while connecting to Tableau: {e}")
    else:
        st.error("Please provide all the necessary credentials.")
