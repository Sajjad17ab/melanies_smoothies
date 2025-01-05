import streamlit as st

# Example login function
def login():
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Replace with real login logic (e.g., checking username and password)
        if username == "admin" and password == "password123":
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid username or password")
            return False
    return False

# Streamlit app layout
def main():
    st.title("Streamlit App with Authentication")

    if login():
        st.write("You are now logged in!")
        # Continue with the rest of the app functionality
    else:
        st.write("Please log in to access the app.")

if __name__ == "__main__":
    main()
