import streamlit as st
import tableauserverclient as TSC
import logging

# Streamlit UI
st.title("Tableau View Exporter")

# Input fields for server details
server = st.text_input("Server address")
site = st.text_input("Site name")
token_name = st.text_input("Personal Access Token name")
token_value = st.text_input("Personal Access Token value", type="password")

# Select the type of export (PDF, PNG, CSV)
export_type = st.radio("Select export type", ("PDF", "PNG", "CSV"))

# File name input
filename = st.text_input("Filename to save exported data", "output")

# Filter field
filter_field = st.text_input("Optional: View filter (COLUMN:VALUE)")

# Select the resource type (view or workbook)
resource_type = st.radio("Select resource type", ("View", "Workbook"))

# Resource ID input (LUID for the view or workbook)
resource_id = st.text_input("Resource ID (LUID)", "")

# Language input (optional)
language = st.text_input("Language (e.g., en, fr, es)", "")

# Logging level (optional)
logging_level = st.selectbox("Logging level", ["debug", "info", "error"])

# Action button to trigger the export
if st.button("Export"):
    # Set up logging
    logging.basicConfig(level=getattr(logging, logging_level.upper()))

    # Tableau Authentication
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site)
    server_connection = TSC.Server(server, use_server_version=True, http_options={"verify": False})
    
    try:
        with server_connection.auth.sign_in(tableau_auth):
            st.write("Connected to Tableau Server.")

            # Determine which resource to export
            if resource_type == "Workbook":
                item = server_connection.workbooks.get_by_id(resource_id)
            else:
                item = server_connection.views.get_by_id(resource_id)

            if not item:
                st.error(f"No item found for ID: {resource_id}")
            else:
                st.write(f"Item found: {item.name}")

                # Determine export options
                if export_type == "PDF":
                    populate_func_name, option_factory_name, member_name, extension = "populate_pdf", "PDFRequestOptions", "pdf", "pdf"
                elif export_type == "PNG":
                    populate_func_name, option_factory_name, member_name, extension = "populate_image", "ImageRequestOptions", "image", "png"
                else:
                    populate_func_name, option_factory_name, member_name, extension = "populate_csv", "CSVRequestOptions", "csv", "csv"

                populate_func = getattr(server_connection.views, populate_func_name)
                option_factory = getattr(TSC, option_factory_name)
                options = option_factory()

                # Apply filter if provided
                if filter_field:
                    options = options.vf(*filter_field.split(":"))

                # Apply language if provided
                if language:
                    options.language = language

                # Set default filename if not provided
                if not filename:
                    filename = f"out-{options.language}.{extension}"

                # Perform the export
                populate_func(item, options)

                # Save to file
                with open(filename, "wb") as f:
                    if member_name == "csv":
                        f.writelines(getattr(item, member_name))
                    else:
                        f.write(getattr(item, member_name))
                
                st.success(f"Export saved as {filename}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
