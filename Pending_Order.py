import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, when_matched

# Snowflake connection parameters
sf_options = {
    "account": "your_account",
    "user": "your_user",
    "password": "your_password",
    "warehouse": "your_warehouse",
    "database": "your_database",
    "schema": "your_schema"
}

# Create the Snowflake session manually
try:
    session = Session.builder.configs(sf_options).create()
except Exception as e:
    st.error(f"Error creating Snowflake session: {e}")
    session = None  # Set session to None if creation fails

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")

# Ensure session was created successfully before proceeding
if session:
    try:
        # Retrieve data as a Snowpark DataFrame, filter by pending orders
        my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0).to_pandas()

        # Check if there are any pending orders
        if not my_dataframe.empty:
            # Display the DataFrame in the data editor
            editable_df = st.data_editor(my_dataframe)
            submitted = st.button('Submit')

            if submitted:
                try:
                    # Convert the edited pandas DataFrame back to a Snowpark DataFrame
                    edited_dataset = session.create_dataframe(editable_df)

                    # Perform the merge operation to update the orders in Snowflake
                    og_dataset = session.table("smoothies.public.orders")

                    # Merge operation on ORDER_UID and update ORDER_FILLED
                    og_dataset.merge(
                        edited_dataset,
                        (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
                        [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )

                    st.success("Order(s) Updated!", icon="👍")
                except Exception as e:
                    st.error(f"Error during update: {e}")
        else:
            st.success("There are no pending orders right now.", icon="👍")
    except Exception as e:
        st.error(f"Error retrieving data: {e}")
else:
    st.error("Could not establish a Snowflake session.")
