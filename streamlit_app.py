import streamlit as st
#from streamlit_gsheets import GSheetsConnection
# Use the following instead:
# First run the command: python3 -m pip install gspread oauth2client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Display Title and Description
st.title("Vendor Management Portal")
st.markdown("Enter the details of the new vendor below.")

# # Establishing a Google Sheets connection
# conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# # Fetch existing vendors data
# existing_data = conn.read(worksheet="Vendors", usecols=list(range(6)), ttl=5)
# existing_data = existing_data.dropna(how="all")

# Alternative Method:
# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name("./.streamlit/credentials.json", scope)

# Authorize the clientsheet 
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("Your Google Sheet Name")

# Get the first sheet of the Spreadsheet
worksheet = sheet.get_worksheet(0)

# Example: Get all values in the first row
existing_data = worksheet.row_values(1)

st.dataframe(existing_data)