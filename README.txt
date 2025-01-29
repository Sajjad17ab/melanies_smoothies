Overview
The Data Entry Application is a simple web app built using Streamlit and Pandas. It allows users to enter data related to customer transactions and saves the entries to an Excel file. The app provides a user-friendly interface for managing data entries, including fields for date, customer name, product name, quantity, unit price, total price, and status.

Features
User-friendly form for data entry.
Automatically calculates total price based on quantity and unit price.
Saves entries to an Excel file.
Displays existing entries in a tabular format.
Basic input validation to ensure required fields are filled.
Requirements
To run this application, you will need:

Python 3.7 or higher
Streamlit
Pandas
openpyxl (for reading and writing Excel files)
You can install the required packages using pip:

bash
Copy
pip install streamlit pandas openpyxl
Getting Started
Clone the Repository:

bash
Copy
git clone <repository-url>
cd <repository-directory>
Run the Application:

Execute the following command to start the Streamlit server:

bash
Copy
streamlit run app.py
Replace app.py with the name of your Python file if it's different.

Access the Application:

Open your web browser and go to http://localhost:8501 to access the Data Entry Application.

How to Use
Fill out the form with the required information:

Entry Date: Select the date of the entry.
Customer Name: Enter the name of the customer.
Product Name: Enter the name of the product.
Quantity: Specify the quantity of the product.
Unit Price: Enter the unit price of the product.
Status: Select the status of the entry (Delivered, Pending, or Cancelled).
Click the "Save Entry" button to save the data. The total price will be calculated automatically based on the quantity and unit price.

Existing entries will be displayed below the form. You can see the total number of records saved.

Data Storage
All entries are stored in an Excel file named data_entries.xlsx located in the same directory as the application script. If the file does not exist, it will be created automatically upon saving the first entry.

Troubleshooting
If you encounter any errors while loading or saving data, ensure that the necessary permissions are set for the directory where the Excel file is being created.
Make sure all required fields are filled in before submitting the form.
Contributing
Feel free to fork the repository and submit pull requests for any enhancements or bug fixes.
