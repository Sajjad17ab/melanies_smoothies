import streamlit as st
import tableauserverclient as TSC
import pandas as pd

# Streamlit UI for user credentials input
st.title("Tableau All Workbooks Details")

# Get Tableau credentials from the user (PAT)
token_name = st.text_input("Enter your Tableau Personal Access Token Name")
token_value = st.text_input("Enter your Tableau Personal Access Token Value", type="password")
site_id = st.text_input("Enter your Tableau Site ID (Leave blank for default site)", value="")
server_url = st.text_input("Enter Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")

# Button to fetch all workbook details
if st.button("Get All Workbook Details"):
    if token_name and token_value and server_url:
        try:
            # Tableau authentication using Personal Access Token (PAT)
            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
            server = TSC.Server(server_url, use_server_version=True)

            with server.auth.sign_in(tableau_auth):
                # Get all workbooks from Tableau Server
                all_workbooks, pagination_item = server.workbooks.get()

                # List to hold details of all workbooks
                workbooks_data = []

                for workbook in all_workbooks:
                    # Get the project for the workbook
                    project = server.projects.get_by_id(workbook.project_id)

                    # Get views associated with the workbook
                    views, _ = server.views.get(workbook)

                    # Get data sources associated with the workbook
                    datasources, _ = server.datasources.get(workbook)

                    # Extract workbook details
                    workbook_details = {
                        "Workbook ID": workbook.id,
                        "Workbook Name": workbook.name,
                        "Project": project.name if project else "N/A",
                        "Owner": workbook.owner_id,
                        "Created At": workbook.created_at,
                        "Modified At": workbook.updated_at,
                        "Content URL": workbook.content_url,
                        "Description": workbook.description,
                        "Tags": ", ".join(workbook.tags) if workbook.tags else "N/A",
                        "Number of Views": len(views),
                        "Number of Data Sources": len(datasources)
                    }

                    workbooks_data.append(workbook_details)

                # Convert the list of workbooks data into a pandas DataFrame
                workbooks_df = pd.DataFrame(workbooks_data)

                # Display workbooks data in a table
                st.subheader("All Workbooks Details:")
                st.dataframe(workbooks_df)

                # Optionally, export to Excel or CSV
                export_option = st.radio("Choose export format:", ("None", "Excel", "CSV"))

                # Export to Excel
                if export_option == "Excel":
                    def to_excel(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Workbooks Data")
                        output.seek(0)
                        return output

                    excel_file = to_excel(workbooks_df)
                    st.download_button(
                        label="Download Excel file",
                        data=excel_file,
                        file_name="all_workbooks_details.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                # Export to CSV
                elif export_option == "CSV":
                    csv_data = workbooks_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV file",
                        data=csv_data,
                        file_name="all_workbooks_details.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"An error occurred while retrieving workbook details: {e}")
    else:
        st.error("Please provide all the necessary credentials.")
