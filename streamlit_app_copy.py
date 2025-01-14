import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# Define the scope for Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("./.streamlit/credentials.json", scope)
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("Student Entry")
worksheet = sheet.get_worksheet(0)

# Fetch existing data from Google Sheets
existing_data = worksheet.get_all_values()
headers = existing_data[0]
pd_existing_data = pd.DataFrame(existing_data[1:], columns=headers)

# Streamlit app setup
st.set_page_config(page_title="Student Schedule", layout="wide")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "View Spreadsheet", "Add Tasks", "Edit Tasks", "Remove Tasks"])

# Home Page
if menu == "Home":
    st.title("Student Schedule Planner")
    st.markdown("""
        Welcome to your Student Schedule app!  
        Navigate using the sidebar to:
        - View Spreadsheet
        - Add Tasks
        - Edit Tasks
        - Remove Tasks
    """)

# View Spreadsheet Page
elif menu == "View Spreadsheet":
    st.title("View Spreadsheet")
    st.dataframe(pd_existing_data)

# Add Tasks Page
elif menu == "Add Tasks":
    st.title("Add a Task")
    # Get existing task names to check for duplicates
    existing_task_names = pd_existing_data["Task Name"].tolist()

    with st.form(key="add_task_form"):
        task_name = st.text_input("Task Name*")
        priority = st.slider("Priority (1-10)", min_value=1, max_value=10)
        status = st.selectbox("Status*", ["Incomplete", "Ongoing", "Complete"])
        start_date = st.date_input("Start Date", value=datetime.date.today())
        due_date = st.date_input("Due Date")
        reminder = st.date_input("Reminder Date", value=datetime.date.today())

        submit_button = st.form_submit_button("Submit Task")

        if submit_button:
            # Ensure task name is provided
            if task_name:  
                # Check if the task name already exists in the list
                if task_name in existing_task_names:
                    st.error("This task name already exists. Please use a different name.")
                else:
                    # Add task to Google Sheet
                    new_task = [task_name, priority, status, start_date, due_date, reminder]
                    worksheet.append_row([str(item) for item in new_task])
                    st.success("Task added successfully!")
            else:
                st.error("Task Name is required.")

# Edit Tasks Page
elif menu == "Edit Tasks":
    st.title("Edit a Task")
    task_names = pd_existing_data["Task Name"].tolist()
    task_to_edit = st.selectbox("Select Task to Edit", options=task_names)

    if task_to_edit:
        # Get the selected task's details
        task_row = pd_existing_data[pd_existing_data["Task Name"] == task_to_edit].index[0] + 2
        task_data = pd_existing_data.iloc[task_row - 2]

        
        task_name = task_data["Task Name"]
        priority = int(task_data["Priority"])
        status = task_data["Status"]
        start_date = datetime.datetime.strptime(task_data["Start Date"], "%Y-%m-%d").date()
        due_date = datetime.datetime.strptime(task_data["Due Date"], "%Y-%m-%d").date() if task_data["Due Date"] else None
        reminder = datetime.datetime.strptime(task_data["Reminder"], "%Y-%m-%d").date()

        with st.form(key="edit_task_form"):
            new_task_name = st.text_input("Task Name*", value=task_name)
            new_priority = st.slider("Priority (1-10)", min_value=1, max_value=10, value=priority)
            new_status = st.selectbox("Status*", ["Incomplete", "Ongoing", "Complete"], index=["Incomplete", "Ongoing", "Complete"].index(status))
            new_start_date = st.date_input("Start Date", value=start_date)
            new_due_date = st.date_input("Due Date", value=due_date)
            new_reminder = st.date_input("Reminder Date", value=reminder)

            save_button = st.form_submit_button("Save Changes")

            if save_button:
                # Update the Google Sheet
                worksheet.update_cell(task_row, 1, new_task_name)
                worksheet.update_cell(task_row, 2, new_priority)
                worksheet.update_cell(task_row, 3, new_status)
                worksheet.update_cell(task_row, 4, new_start_date.strftime("%Y-%m-%d"))
                worksheet.update_cell(task_row, 5, new_due_date.strftime("%Y-%m-%d") if new_due_date else "")
                worksheet.update_cell(task_row, 6, new_reminder.strftime("%Y-%m-%d"))

                st.success("Task updated successfully!")

# Remove Tasks Page
elif menu == "Remove Tasks":
    st.title("Remove a Task")
    task_names = pd_existing_data["Task Name"].tolist()
    task_to_remove = st.selectbox("Select Task to Remove", options=task_names)
    
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