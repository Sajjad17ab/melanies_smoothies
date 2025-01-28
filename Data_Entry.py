import streamlit as st
import pandas as pd
from datetime import date

# Configure the page
st.set_page_config(
    page_title="Data Entry App",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Excel file path
EXCEL_FILE = "data_entries.xlsx"

def load_data():
    """Load existing data from Excel or create new DataFrame"""
    try:
        return pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Date", "Customer Name", "Product Name", 
            "Quantity", "Unit Price", "Total Price", "Status"
        ])

def save_data(df):
    """Save DataFrame to Excel file"""
    df.to_excel(EXCEL_FILE, index=False)

# Main app interface
st.title("📝 Data Entry Application")

# Create input form
with st.form("data_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        entry_date = st.date_input("Entry Date", value=date.today())
        customer_name = st.text_input("Customer Name")
        product_name = st.text_input("Product Name")
        
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1)
        unit_price = st.number_input("Unit Price ($)", min_value=0.0, value=0.0)
        total_price = quantity * unit_price
        status = st.selectbox("Status", options=["Delivered", "Pending", "Cancelled"])
    
    st.markdown(f"**Total Price:** ${total_price:,.2f}")
    
    submitted = st.form_submit_button("Save Entry")
    
    if submitted:
        if not customer_name or not product_name:
            st.error("Please fill in all required fields (Customer Name and Product Name)")
        else:
            new_entry = pd.DataFrame([{
                "Date": entry_date,
                "Customer Name": customer_name,
                "Product Name": product_name,
                "Quantity": quantity,
                "Unit Price": unit_price,
                "Total Price": total_price,
                "Status": status
            }])
            
            df = load_data()
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success("Entry saved successfully!")

# Display existing data
st.header("📋 Saved Entries")
df = load_data()

if not df.empty:
    st.dataframe(
        df.style.format({
            "Unit Price": "${:.2f}",
            "Total Price": "${:.2f}"
        }),
        use_container_width=True
    )
    st.markdown(f"**Total Records:** {len(df)}")
else:
    st.info("No entries found. Start adding data using the form above.")