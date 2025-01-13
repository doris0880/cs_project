import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# Display Title and Description
st.title("Student Schedule")
st.markdown("Enter the details of your schedule below.")

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name("./.streamlit/credentials.json", scope)
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("Student Entry")

# Get the first sheet of the Spreadsheet
worksheet = sheet.get_worksheet(0)

# Fetch and convert Google Sheets data to a DataFrame
existing_data = worksheet.get_all_values()
if existing_data:  # Ensure there is data
    pd_existing_data = pd.DataFrame(existing_data[1:], columns=existing_data[0])  # Skip the header row
else:
    pd_existing_data = pd.DataFrame(columns=["Task Name", "Priority", "Status", "Start Date", "Due Date", "Reminder"])  # Empty DataFrame

# List of Status Types
STATUS_TYPES = [
    "Incomplete",
    "Ongoing",
    "Complete",
]

# New Schedule Form
with st.form(key="schedule_form"):
    task_name = st.text_input(label="Task Name*")
    priority = st.slider(label="Level of Priority", min_value=1, max_value=10)
    status = st.selectbox(label="Status*", options=STATUS_TYPES)
    start_date = st.date_input(label="Start Date", value=datetime.date.today())
    due_date = st.date_input(label="Due Date", value=None)
    reminder = st.date_input(label="Reminder Date", value=datetime.date.today(), min_value=datetime.date.today())
    
    # Mark all mandatory fields
    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit Task")
    # If the submit button is pressed
    if submit_button:
        # Check all mandatory fields are filled
        if not task_name or not status:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        else:
            # Create a new row of task data
            task_data = pd.DataFrame(
                [
                    {
                        "Task Name": task_name,
                        "Priority": priority,
                        "Status": status,
                        "Start Date": start_date.strftime("%Y-%m-%d"),
                        "Due Date": due_date.strftime("%Y-%m-%d") if due_date else "",
                        "Reminder": reminder.strftime("%Y-%m-%d"),
                    }
                ]
            )
            
            # Convert the first row to a list and ensure all data types are serializable
            task_data_list = task_data.iloc[0].apply(str).tolist()  # Convert everything to string
            
            # Append the task data to Google Sheets
            worksheet.append_row(task_data_list)

            st.success("Task details successfully submitted!")
