import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title('Available Study Sessions')

st.write('\n\n')
st.write('## Model 1 Maintenance')


st.write("## All Upcoming Study Sessions")

if st.button("Search Prediction", type="primary", use_container_width=True):
    try:
        # API call to get all study sessions
        url = "http://localhost:4000/sessions"
        response = requests.get(url)
        sessions = response.json()
        
        if sessions:
            st.success(f"Found {len(sessions)} study sessions!")
            # Convert to DataFrame for better display
            df = pd.DataFrame(sessions)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No study sessions found.")
    except Exception as e:
        st.error(f"Error loading sessions: {e}")


st.write("## Search by Location")

building = st.text_input("Enter building name:", "")
room = st.text_input("Enter room number:", "")

if st.button("Search by Location", use_container_width=True):
    try:
        url = f"http://localhost:4000/sessions/location?building={building}&room={room}"
        results = requests.get(url).json()
        st.success("Prediction retrieved!")
        st.dataframe(results)
    except:
        st.error("Please enter values correctly, like `10, 25`.")


st.write("## Search by Date")

# Example: converting API results into coordinates
# Modify depending on your API output format
if st.checkbox("Show Prediction Map"):
    try:
        url = f"http://localhost:4000/sessions/date/{session_date}"
        results = requests.get(url).json()
        
        if results:
            st.success(f"Found {len(results)} sessions on {session_date}")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("No sessions found for this date.")
    except Exception as e:
        st.error(f"Error: {e}")


st.write("## Search by Course")

crn_input = st.text_input("Enter Course CRN:", value="12345", max_chars=5)  # ✅ Changed to text_input

if st.button("Search by Course", use_container_width=True):
    try:
        crn = int(crn_input)  # Convert to integer
        url = f"http://localhost:4000/sessions/course/{crn}"
        results = requests.get(url).json()
        
        if results:
            st.success(f"Found sessions for CRN {crn}")
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.info("No sessions found for this course.")
    except ValueError:
        st.error("Please enter a valid CRN number")
    except Exception as e:
        st.error(f"Error: {e}")




st.write("## View Session Details")

session_id_input = st.text_input("Enter Session ID:", value="1001", max_chars=4, key="detail_id")  # ✅ Changed to text_input

if st.button("Get Session Details", use_container_width=True):
    try:
        session_id = int(session_id_input)  # Convert to integer
        url = f"http://localhost:4000/sessions/{session_id}"
        session = requests.get(url).json()
        
        if session:
            st.success("Session found!")
            
            # Display session info
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Session Information:**")
                st.write(f"Session ID: {session.get('sessionID')}")
                st.write(f"Date: {session.get('date')}")
                st.write(f"Start Time: {session.get('startTime')}")
                st.write(f"End Time: {session.get('endTime')}")
            
            with col2:
                st.write("**Location:**")
                st.write(f"Building: {session.get('building')}")
                st.write(f"Room: {session.get('room')}")
                st.write(f"Capacity: {session.get('capacity')}")
            
            # Get topics covered
            topics_url = f"http://localhost:4000/sessions/{session_id}/topics"
            topics = requests.get(topics_url).json()
            
            if topics:
                st.write("**Topics Covered:**")
                for topic in topics:
                    st.write(f"- {topic.get('name')}")
            
            # Get attending TAs
            tas_url = f"http://localhost:4000/sessions/{session_id}/tas"
            tas = requests.get(tas_url).json()
            
            if tas:
                st.write("**Teaching Assistants:**")
                for ta in tas:
                    st.write(f"- {ta.get('firstName')} {ta.get('lastName')}")
        else:
            st.warning("Session not found.")
    except ValueError:
        st.error("Please enter a valid Session ID number")
    except Exception as e:
        st.error(f"Error: {e}")
