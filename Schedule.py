import streamlit as st
import tableauserverclient as TSC
import logging
from datetime import time


# Function to create schedules
def create_schedule(server, tableau_auth, schedule_type, interval_value, start_time, end_time=None, days=None):
    try:
        # Choose schedule type
        if schedule_type == "Hourly":
            interval = TSC.HourlyInterval(start_time=start_time, end_time=end_time, interval_value=interval_value)
            schedule = TSC.ScheduleItem(
                "Hourly-Schedule",
                50,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Parallel,
                interval,
            )
        elif schedule_type == "Daily":
            interval = TSC.DailyInterval(start_time=start_time)
            schedule = TSC.ScheduleItem(
                "Daily-Schedule",
                60,
                TSC.ScheduleItem.Type.Subscription,
                TSC.ScheduleItem.ExecutionOrder.Serial,
                interval,
            )
        elif schedule_type == "Weekly":
            interval = TSC.WeeklyInterval(start_time=start_time, *days)
            schedule = TSC.ScheduleItem(
                "Weekly-Schedule",
                70,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Serial,
                interval,
            )
        elif schedule_type == "Monthly":
            interval = TSC.MonthlyInterval(start_time=start_time, interval_value=interval_value)
            schedule = TSC.ScheduleItem(
                "Monthly-Schedule",
                80,
                TSC.ScheduleItem.Type.Subscription,
                TSC.ScheduleItem.ExecutionOrder.Parallel,
                interval,
            )

        # Create schedule
        created_schedule = server.schedules.create(schedule)
        st.success(f"{schedule_type} schedule created (ID: {created_schedule.id}).")

    except Exception as e:
        st.error(f"Error creating {schedule_type} schedule: {str(e)}")


def main():
    # Set up Streamlit UI
    st.title("Tableau Schedule Creator")

    # User inputs for Tableau authentication
    server_url = st.text_input("Tableau Server URL", value="https://prod-apnortheast-a.online.tableau.com")
    site_id = st.text_input("Tableau Site ID (Leave blank for default site)", value="")
    token_name = st.text_input("Tableau Personal Access Token Name")
    token_value = st.text_input("Tableau Personal Access Token Value", type="password")

    # Choose schedule type
    schedule_type = st.selectbox("Select Schedule Type", ["Hourly", "Daily", "Weekly", "Monthly"])

    # Common scheduling parameters
    interval_value = st.number_input("Interval Value (e.g., 2 for Hourly)", min_value=1, value=2)
    start_time = st.time_input("Start Time", value=time(2, 30))
    end_time = None
    if schedule_type == "Hourly":
        end_time = st.time_input("End Time", value=time(23, 0))
    
    days = []
    if schedule_type == "Weekly":
        days_input = st.multiselect("Select Days (for Weekly Schedule)", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        days = [getattr(TSC.IntervalItem.Day, day.capitalize()) for day in days_input]

    # Button to create schedule
    if st.button("Create Schedule"):
        if server_url and token_name and token_value:
            tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id=site_id)
            server = TSC.Server(server_url, use_server_version=False)
            server.add_http_options({"verify": False})
            server.use_server_version()
            with server.auth.sign_in(tableau_auth):
                create_schedule(server, tableau_auth, schedule_type, interval_value, start_time, end_time, days)
        else:
            st.error("Please provide all required Tableau credentials (Server URL, Token Name, Token Value).")


if __name__ == "__main__":
    main()
