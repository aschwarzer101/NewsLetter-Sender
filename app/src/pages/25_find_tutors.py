import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(layout='wide')

SideBarLinks()

st.title('📚 Available Study Sessions')

# ============================================
# 1. Display All Upcoming Study Sessions
# ============================================
st.write("## All Upcoming Study Sessions")

if st.button("Load All Sessions", type="primary", use_container_width=True):
    try:
        url = "http://web-api:4000/sessions"
        response = requests.get(url)
        sessions = response.json()
        
        if sessions and len(sessions) > 0:
            st.success(f"Found {len(sessions)} study sessions!")
            df = pd.DataFrame(sessions)
            
            # Format datetime columns
            if 'startTime' in df.columns:
                df['startTime'] = pd.to_datetime(df['startTime']).dt.strftime('%I:%M %p')
            if 'endTime' in df.columns:
                df['endTime'] = pd.to_datetime(df['endTime']).dt.strftime('%I:%M %p')
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No study sessions found.")
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

st.write("---")

# ============================================
# 2. Search Sessions
# ============================================
st.write("## 🔍 Search Sessions")

search_option = st.radio("Search by:", ["Location", "Date", "Session ID"], horizontal=True)

if search_option == "Location":
    col1, col2 = st.columns(2)
    with col1:
        building = st.selectbox("Building:", 
                               ["All Buildings", "Snell Library", "Curry Student Center", 
                                "Forsyth Building", "Ryder Hall"])
    with col2:
        room = st.text_input("Room (optional):", "")
    
    if st.button("Search", use_container_width=True):
        try:
            building_param = "" if building == "All Buildings" else building
            url = f"http://web-api:4000/sessions/location?building={building_param}&room={room}"
            results = requests.get(url).json()
            
            if results and len(results) > 0:
                st.success(f"Found {len(results)} sessions!")
                df = pd.DataFrame(results)
                if 'startTime' in df.columns:
                    df['startTime'] = pd.to_datetime(df['startTime']).dt.strftime('%I:%M %p')
                if 'endTime' in df.columns:
                    df['endTime'] = pd.to_datetime(df['endTime']).dt.strftime('%I:%M %p')
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No sessions found.")
        except Exception as e:
            st.error(f"Error: {e}")

elif search_option == "Date":
    session_date = st.date_input("Select date:", datetime.now())
    
    if st.button("Search", use_container_width=True):
        try:
            url = f"http://web-api:4000/sessions/date/{session_date}"
            results = requests.get(url).json()
            
            if results and len(results) > 0:
                st.success(f"Found {len(results)} sessions!")
                df = pd.DataFrame(results)
                if 'startTime' in df.columns:
                    df['startTime'] = pd.to_datetime(df['startTime']).dt.strftime('%I:%M %p')
                if 'endTime' in df.columns:
                    df['endTime'] = pd.to_datetime(df['endTime']).dt.strftime('%I:%M %p')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No sessions found for this date.")
        except Exception as e:
            st.error(f"Error: {e}")

else:  # Session ID
    session_id_input = st.text_input("Enter Session ID:", value="1001", max_chars=4)  # ✅ Changed
    
    if st.button("Get Details", use_container_width=True):
        try:
            session_id = int(session_id_input)  # Convert to integer
            url = f"http://web-api:4000/sessions/{session_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                session = response.json()
                
                if session and 'sessionID' in session:
                    st.success("Session found!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**📅 Session Info:**")
                        st.write(f"Date: {session.get('date', 'N/A')}")
                        if session.get('startTime'):
                            st.write(f"Time: {pd.to_datetime(session['startTime']).strftime('%I:%M %p')} - {pd.to_datetime(session.get('endTime')).strftime('%I:%M %p')}")
                    
                    with col2:
                        st.write("**🏢 Location:**")
                        st.write(f"{session.get('building', 'N/A')} - Room {session.get('room', 'N/A')}")
                        st.write(f"Capacity: {session.get('capacity', 'N/A')}")
                    
                    with col3:
                        st.write("**📊 Status:**")
                        status = "✅ Available" if session.get('status') == 1 else "❌ Unavailable"
                        st.write(status)
                    
                    st.write("---")
                    
                    # Topics
                    topics_url = f"http://web-api:4000/sessions/{session_id}/topics"
                    topics_response = requests.get(topics_url)
                    if topics_response.status_code == 200:
                        topics = topics_response.json()
                        if topics:
                            st.write("**📚 Topics:**")
                            for topic in topics:
                                st.write(f"• {topic.get('name', 'Unknown')}")
                    
                    # TAs
                    tas_url = f"http://web-api:4000/sessions/{session_id}/tas"
                    tas_response = requests.get(tas_url)
                    if tas_response.status_code == 200:
                        tas = tas_response.json()
                        if tas:
                            st.write("**👨‍🏫 TAs:**")
                            for ta in tas:
                                st.write(f"• {ta.get('firstName', '')} {ta.get('lastName', '')}")
                else:
                    st.warning("Session not found.")
            else:
                st.error("Session not found.")
        except ValueError:
            st.error("Please enter a valid Session ID number")
        except Exception as e:
            st.error(f"Error: {e}")

st.write("---")

# ============================================
# 3. Join/Leave Session
# ============================================
st.write("## 👥 Join or Leave a Session")

col1, col2 = st.columns(2)

with col1:
    student_nuid_input = st.text_input("Your NUID:", value="002345678", max_chars=9)  # ✅ Changed

with col2:
    action_session_id_input = st.text_input("Session ID:", value="1001", max_chars=4, key="action_session")  # ✅ Changed

join_col, leave_col = st.columns(2)

with join_col:
    if st.button("Join Session", type="primary", use_container_width=True):
        try:
            student_nuid = int(student_nuid_input)  # Convert to integer
            action_session_id = int(action_session_id_input)  # Convert to integer
            
            url = f"http://web-api:4000/sessions/{action_session_id}/join"
            data = {"nuID": student_nuid}
            response = requests.post(url, json=data)
            
            if response.status_code == 201:
                st.success("✅ Successfully joined!")
            elif response.status_code == 400:
                st.warning(response.json().get('error', 'Already enrolled'))
            else:
                st.error("Error joining session")
        except ValueError:
            st.error("Please enter valid numbers")
        except Exception as e:
            st.error(f"Error: {e}")

with leave_col:
    if st.button("Leave Session", use_container_width=True):
        try:
            student_nuid = int(student_nuid_input)  # Convert to integer
            action_session_id = int(action_session_id_input)  # Convert to integer
            
            url = f"http://web-api:4000/sessions/{action_session_id}/leave"
            data = {"nuID": student_nuid}
            response = requests.delete(url, json=data)
            
            if response.status_code == 200:
                st.success("✅ Successfully left!")
            else:
                st.warning("Not enrolled in this session")
        except ValueError:
            st.error("Please enter valid numbers")
        except Exception as e:
            st.error(f"Error: {e}")