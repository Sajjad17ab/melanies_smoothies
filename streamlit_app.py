# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col
# Write directly to the app
st.title(":cup_with_straw: Custome Your Smoothie!:cup_with_straw:")
st.write(
    """Chose the Fruits you want in your Custome Smoothie!
    """
)
name_on_order = st.text_input("Name on Smoothie :")
st.write("The Name on Smoothie will be :", name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

Ingredients_List = st.multiselect(
    "Chose Upto 5 Ingredients:",
    my_dataframe,
    max_selections=5
)


if Ingredients_List:
    Ingredients_string=''

    for fruit_chosen in Ingredients_List:
        Ingredients_string += fruit_chosen +' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)


    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
            values ('""" + Ingredients_string + """','"""+name_on_order+"""')"""
    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}', icon="✅")


