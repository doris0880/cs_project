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
creds = ServiceAccountCredentials.from_json_keyfile_name("./.streamlit/credentials.json", scope)

# Authorize the client sheet
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("Student Entry")

# Get the first sheet of the Spreadsheet
worksheet = sheet.get_worksheet(0)

# Fetch existing data from Google Sheets
existing_data = worksheet.get_all_values()

# Extract headers from the first row
headers = existing_data[0]

# Convert the rest of the data to a DataFrame using the headers from the first row
pd_existing_data = pd.DataFrame(existing_data[1:], columns=headers)

# Display existing data in Streamlit
st.dataframe(pd_existing_data)

# List of Status Types
STATUS_TYPES = [
    "Incomplete",
    "Ongoing",
    "Complete",
]
# Add Task Header
st.subheader("Add a Task")
# New Schedule Form
with st.form(key="schedule_form"):
    task_name = st.text_input(label="Task Name*")
    priority = st.slider(label="Level of Priority", min_value=1, max_value=10)
    status = st.selectbox(label="Status*", options=STATUS_TYPES)
    start_date = st.date_input(label="Start Date", value=datetime.date.today())
    due_date = st.date_input(label="Due Date", value=None)
    reminder = st.date_input(label="Reminder Date", value=datetime.date.today(), min_value=datetime.date.today())

    # Mark all required fields
    st.markdown("**required*")
    # Submit button
    submit_button = st.form_submit_button(label="Submit Task")

    if submit_button:
        # Check mandatory fields
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
            task_data_list = task_data.iloc[0].astype(str).tolist()

            # Update Google Sheets with new task data
            worksheet.append_row(task_data_list)
            st.success("Task details successfully submitted!")

# Task Deletion: Display tasks in a dropdown
st.subheader("Remove a Task")

# Use a selectbox to choose the task to remove
task_names = pd_existing_data["Task Name"].tolist()
task_to_remove = st.selectbox("Select a Task to Remove", options=task_names)

# Add a button to delete the selected task
if st.button("Delete Task"):
    if task_to_remove:
        # Find the row index for the selected task
        task_row = int(pd_existing_data[pd_existing_data["Task Name"] == task_to_remove].index[0]) + 2
        # Delete the row in the sheet
        worksheet.delete_rows(task_row)  
        st.success(f"Task '{task_to_remove}' successfully removed!")
    # Warn users about deletion
    else:
        st.warning("Please select a task to delete.")