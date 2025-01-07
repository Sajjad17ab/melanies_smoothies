import streamlit as st
import tableauserverclient as TSC

# Set up connection.
tableau_auth = TSC.PersonalAccessTokenAuth(
    st.secrets["tableau"]["token_name"],
    st.secrets["tableau"]["personal_access_token"],
    st.secrets["tableau"]["site_id"],
)
server = TSC.Server(st.secrets["tableau"]["server_url"], use_server_version=True)

# USERNAME = 'xufimail@keemail.me'
# PASSWORD = 'Merimarzi67@'
# SITENAME = 'xufimail-786e7560ed'
# URL = 'https://prod-apnortheast-a.online.tableau.com'

# tableau_auth = TSC.TableauAuth('xufimail@keemail.me', 'Merimarzi67@', 'xufimail-786e7560ed')
# server = TSC.Server('https://prod-apnortheast-a.online.tableau.com')

with server.auth.sign_in(tableau_auth):
    all_users, pagination_item = server.users.get()
    st.write(f"\nThere are {pagination_item.total_available} users on site:")
    st.write([user.name for user in all_users])

    all_datasources, pagination_item_ds = server.datasources.get()
    all_workbooks_items, pagination_item_wb = server.workbooks.get()

    st.write(f"\nThere are {pagination_item_ds.total_available} datasources on site:")
    st.write([datasource.name for datasource in all_datasources])
    st.write([datasource.id for datasource in all_datasources])

    st.write(f"\nThere are {pagination_item_wb.total_available} workbooks on site:")
    st.write([workbook.name for workbook in all_workbooks_items])
    st.write([workbook.id for workbook in all_workbooks_items])
