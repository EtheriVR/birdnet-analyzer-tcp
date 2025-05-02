import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, time
import time as unixtime
def get_recent_bird() -> str:
    try:
        payload = {
            "from": int(unixtime.time()-3600),
            "to": int(unixtime.time())
        }
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[-1]['name']
    except:
        return "zzz"



# --- Configuration ---
API_URL = "http://0.0.0.0:8080/birds" # The endpoint to fetch data from

# --- Streamlit App Layout ---
st.set_page_config(layout="wide") # Use wide layout for better table display
bird ="Test"
st.title(f"You are listening to the: { get_recent_bird() }")

# --- Date Input ---
# Use columns for better layout
col1, col2 = st.columns(2)

with col1:
    # Get start date input from the user, default to today
    from_date = st.date_input("From Date", value=date.today())
    from_t = st.time_input("",time(0, 0))
with col2:
    # Get end date input from the user, default to today
    to_date = st.date_input("To Date", value=date.today())
    to_t = st.time_input("",key="timeto")

# Combine date with time to create datetime objects (start of day for 'from', end of day for 'to')
# API might expect full timestamps, adjust format if needed (e.g., including time)
from_datetime = datetime.combine(from_date, from_t)
to_datetime = datetime.combine(to_date, to_t)

# --- Fetch Button and Data Display ---
if st.button("Fetch Bird Data"):
    # Validate date range
    if from_datetime > to_datetime:
        st.error("Error: 'From Date' cannot be after 'To Date'. Please select a valid range.")
    else:
        # Prepare the JSON payload for the POST request
        # Convert datetime objects to ISO 8601 string format (e.g., "2025-04-29T00:00:00")
        # Adjust the format string if the API expects something different (e.g., Unix timestamp)
        payload = {
            "from": int(from_datetime.timestamp()),
            "to": int(to_datetime.timestamp())
        }

        #st.write(f"Fetching data from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}...")
        #st.write("Sending payload:", payload) # Display payload for debugging

        try:
            # Make the POST request to the API
            response = requests.post(API_URL, json=payload, timeout=10) # Added timeout

            # Check if the request was successful (status code 200)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            # Parse the JSON response
            try:
                data = response.json()

                # Check if data is a list and not empty
                if isinstance(data, list) and data:
                    # Convert the list of dictionaries to a Pandas DataFrame
                    # Assuming the JSON looks like: [{"name": "Robin", "date": "2023-10-27T10:00:00"}, ...]
                    df = pd.DataFrame(data)

                    # Ensure required columns 'name' and 'date' exist
                    if 'name' in df.columns and 'created_at' in df.columns:
                         # Display the data in a table
                        st.subheader("Fetched Bird Data")
                        st.dataframe(df[['name', 'created_at']], use_container_width=True) # Select and display only name and date
                    else:
                        st.warning("Response JSON structure is not as expected. Missing 'name' or 'date' fields.")
                        st.json(data) # Show the raw data for inspection

                elif isinstance(data, list) and not data:
                    st.info("No bird data found for the selected date range.")
                else:
                    st.warning("Received unexpected data format from API.")
                    st.json(data) # Show the raw data

            except ValueError:
                # Handle JSON decoding error
                st.error("Error: Could not decode JSON response from the API.")
                st.text(response.text) # Show raw response text

        except requests.exceptions.ConnectionError:
            st.error(f"Error: Could not connect to the API at {API_URL}. Is the server running?")
        except requests.exceptions.Timeout:
            st.error("Error: The request to the API timed out.")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e.response.status_code} {e.response.reason}")
            st.text(f"Response body: {e.response.text}") # Show error response body
        except requests.exceptions.RequestException as e:
            # Handle other potential request errors
            st.error(f"An error occurred during the API request: {e}")

# --- Footer ---
st.markdown("---")


