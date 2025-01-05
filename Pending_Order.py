# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")

session = get_active_session()

# Retrieve data as a Snowpark DataFrame, filter by pending orders
my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0).to_pandas()

# Check if there are any pending orders
if not my_dataframe.empty:
    # Display the DataFrame in the data editor
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')

    if submitted:
        # Convert the edited pandas DataFrame back to a Snowpark DataFrame
        edited_dataset = session.create_dataframe(editable_df)

        try:
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
            st.error(f"Something went wrong: {e}")

else:
    st.success("There are no pending orders right now.", icon="👍")
