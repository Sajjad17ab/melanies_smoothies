import streamlit as st
import tableauserverclient as TSC
import logging
import csv

# Streamlit UI
st.title("Tableau View Exporter - Login & Export Workbooks Data")

# Input fields for server details
server = st.text_input("Server address")
site = st.text_input("Site name")
token_name = st.text_input("Personal Access Token name")
token_value = st.text_input("Personal Access Token value", type="password")

# Logging level (optional)
logging_level = st.selectbox("Logging level", ["debug", "info", "error"])

# Action button to trigger the login and export
if st.button("Test Login and Export Workbooks Data"):
    # Set up logging
    logging.basicConfig(level=getattr(logging, logging_level.upper()))

    # Tableau Authentication
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site)
    server_connection = TSC.Server(server, use_server_version=True, http_options={"verify": False})

    try:
        # Attempt to sign in
        with server_connection.auth.sign_in(tableau_auth):
            st.write("Connected to Tableau Server successfully!")

            # Retrieve all workbooks and their details
            all_workbooks, pagination_item = server_connection.workbooks.get()

            # List to store workbook, data source, and owner information
            workbook_data = []

            for workbook in all_workbooks:
                # Get the workbook's owner
                owner_name = workbook.owner.name if workbook.owner else "Unknown"
                
                # Retrieve data sources associated with this workbook
                server_connection.workbooks.populate_data_sources(workbook)
                
                # Loop through data sources for the workbook
                for data_source in workbook.datasources:
                    workbook_data.append([workbook.name, data_source.name, owner_name])

            # Export the collected data to a CSV file
            filename = "workbooks_data.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Workbook Name", "Data Source Name", "Owner"])
                writer.writerows(workbook_data)

            # Notify the user of the successful export
            st.success(f"Exported workbook data to {filename}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
