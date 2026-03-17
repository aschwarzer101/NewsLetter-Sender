# import logging
# logger = logging.getLogger(__name__)
# import pandas as pd
# import streamlit as st
# from streamlit_extras.app_logo import add_logo
# import world_bank_data as wb
# import matplotlib.pyplot as plt
# import numpy as np
# import plotly.express as px
# from modules.nav import SideBarLinks
# import requests 

# # Call the SideBarLinks from the nav module in the modules directory
# SideBarLinks()

# st.header('Student Analytics Dashboard') 

# courses = requests.get('http://web-api:4000/cr/course').json()
# selected_course = st.selectbox("Select a course to view analytics:", courses, format_func = lambda x: f"{x['course_name']} CRN: {x['crn']}")

# st.write("---")

# # See topics students are working on [Professor-6]
# st.subheader("Topics Students are Working On")
# topics_response = requests.get(
#     f"http://web-api:4000/s/study_time/professor/{st.session_state['professor_id']}/topics"
# )
# study_time_data = topics_response.json()

# if study_time_data:
#     df_study = pd.DataFrame(study_time_data)

#     fig = px.bar(df_study, x = 'Topic', y = 'Total_Study_Time',
#     title = f"Total Study Time by Topic for {selected_course['course_name']}",
#     labels = {'Total_Study_Time': 'Total Study Time (minutes)', 'Topic': 'Topic'})
#     st.plotly_chart(fig, use_container_width=True)

# st.dataframe(df_study, use_container_width=True)

# st.subheader("Session Details")
# selected_topic = st.selectbox("View sessions for topic:", df_study['Topic'].tolist())

# sessions = requests.get(f'http://web-api:4000/s/sessions/topic/{selected_topic}').json()

# for session in sessions:
#     with st.expander(f"Session {session['sessionID']} - {session['date']}"):
#             session_details = requests.get(f'http://web-api:4000/s/study_session/{session["sessionID"]}').json()
#             st.json(session_details)
# else:
#     st.info("No study session data available yet")


import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from modules.nav import SideBarLinks
import requests 

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

st.header('📊 Student Analytics Dashboard') 

# API base URL
API_URL = "http://web-api:4000"

# Helper function for API calls with error handling
def make_api_call(method, endpoint, **kwargs):
    """Make API call with proper error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.request(method, url, timeout=5, **kwargs)
        
        if response.status_code >= 400:
            st.error(f"API Error {response.status_code}: {response.text[:200]}")
            return None
            
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            st.error(f"Invalid JSON response from {endpoint}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please check if the API container is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# Get professor ID from session state (with fallback for testing)
prof_id = st.session_state.get('prof_id', 1001)
st.write(f"### Hi, {st.session_state.get('first_name', 'Professor')}.")

# Get all courses
courses = make_api_call('GET', '/cr/course')

if not courses:
    st.warning("No courses found or unable to connect to API")
    st.stop()

# Select course
selected_course = st.selectbox(
    "Select a course to view analytics:", 
    courses, 
    format_func=lambda x: f"{x.get('name', 'Unknown')} - {x.get('department', '')} {x.get('courseNum', '')} (CRN: {x.get('CRN', 'N/A')})"
)

st.write("---")

# ==============================================================================
# SECTION 1: COURSE OVERVIEW METRICS
# ==============================================================================
st.subheader("📋 Course Overview")

col1, col2, col3, col4 = st.columns(4)

# Get topics
topics = make_api_call('GET', f'/cr/topic?crn={selected_course["CRN"]}')
num_topics = len(topics) if topics else 0

# Get enrollments
enrollments = make_api_call('GET', f'/cr/course/{selected_course["CRN"]}/enrollments')
num_students = len(enrollments) if enrollments else 0

# Get resources
resources = make_api_call('GET', f'/cr/resources?crn={selected_course["CRN"]}')
num_resources = len(resources) if resources else 0

# Get TAs
tas = make_api_call('GET', f'/pa/teaching_assistants?crn={selected_course["CRN"]}')
num_tas = len(tas) if tas else 0

with col1:
    st.metric("👥 Enrolled Students", num_students)

with col2:
    st.metric("📖 Topics", num_topics)

with col3:
    st.metric("📚 Resources", num_resources)

with col4:
    st.metric("👨‍🏫 Teaching Assistants", num_tas)

st.write("---")

# ==============================================================================
# SECTION 2: STUDENT ENROLLMENT ANALYSIS
# ==============================================================================
st.subheader("👥 Student Enrollment Analysis")

if enrollments:
    df_enrollments = pd.DataFrame(enrollments)
    
    if not df_enrollments.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Students by Year Chart
            if 'year' in df_enrollments.columns:
                year_counts = df_enrollments['year'].value_counts().sort_index().reset_index()
                year_counts.columns = ['year', 'count']
                
                fig_year = px.bar(
                    year_counts,
                    x='year',
                    y='count',
                    title='Students by Academic Year',
                    labels={'year': 'Academic Year', 'count': 'Number of Students'},
                    color='count',
                    color_continuous_scale='blues',
                    text='count'
                )
                fig_year.update_traces(textposition='outside')
                fig_year.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.info("Year data not available")
        
        with col2:
            # Students by Section Chart
            if 'sectionNum' in df_enrollments.columns:
                section_counts = df_enrollments['sectionNum'].value_counts().reset_index()
                section_counts.columns = ['section', 'count']
                section_counts = section_counts.sort_values('section')
                
                fig_section = px.pie(
                    section_counts,
                    values='count',
                    names='section',
                    title='Students by Section',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_section.update_traces(textposition='inside', textinfo='percent+label')
                fig_section.update_layout(height=400)
                st.plotly_chart(fig_section, use_container_width=True)
            else:
                st.info("Section data not available")
        
        # Students by Semester
        if 'semester' in df_enrollments.columns:
            semester_counts = df_enrollments['semester'].value_counts().reset_index()
            semester_counts.columns = ['semester', 'count']
            
            fig_semester = px.bar(
                semester_counts,
                x='semester',
                y='count',
                title='Students by Semester',
                labels={'semester': 'Semester', 'count': 'Number of Students'},
                color='count',
                color_continuous_scale='greens',
                text='count'
            )
            fig_semester.update_traces(textposition='outside')
            fig_semester.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_semester, use_container_width=True)
        
        # Detailed Student List (Expandable)
        with st.expander("📋 View Detailed Student List"):
            display_cols = ['firstName', 'lastName', 'email', 'year', 'semester', 'sectionNum']
            available_cols = [col for col in display_cols if col in df_enrollments.columns]
            
            if available_cols:
                st.dataframe(
                    df_enrollments[available_cols].rename(columns={
                        'firstName': 'First Name',
                        'lastName': 'Last Name',
                        'email': 'Email',
                        'year': 'Year',
                        'semester': 'Semester',
                        'sectionNum': 'Section'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No students enrolled in this course yet")
else:
    st.info("Unable to load enrollment data")

st.write("---")

# ==============================================================================
# SECTION 3: COURSE RESOURCES ANALYSIS
# ==============================================================================
st.subheader("📚 Course Resources Analysis")

if resources:
    df_resources = pd.DataFrame(resources)
    
    if not df_resources.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Resource Type Distribution
            if 'type' in df_resources.columns:
                type_counts = df_resources['type'].value_counts().reset_index()
                type_counts.columns = ['type', 'count']
                
                fig_type = px.pie(
                    type_counts,
                    values='count',
                    names='type',
                    title='Resource Distribution by Type',
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    hole=0.4
                )
                fig_type.update_traces(textposition='outside', textinfo='percent+label+value')
                fig_type.update_layout(height=400)
                st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            # Resources Uploaded Over Time
            if 'dateUploaded' in df_resources.columns:
                df_resources['dateUploaded'] = pd.to_datetime(df_resources['dateUploaded'])
                df_resources['upload_month'] = df_resources['dateUploaded'].dt.to_period('M').astype(str)
                
                uploads_over_time = df_resources.groupby('upload_month').size().reset_index()
                uploads_over_time.columns = ['month', 'count']
                
                fig_timeline = px.line(
                    uploads_over_time,
                    x='month',
                    y='count',
                    title='Resources Uploaded Over Time',
                    labels={'month': 'Month', 'count': 'Number of Uploads'},
                    markers=True
                )
                fig_timeline.update_traces(line_color='#FF6B6B', line_width=3, marker=dict(size=10))
                fig_timeline.update_layout(height=400)
                st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Resource upload activity heatmap
        if 'dateUploaded' in df_resources.columns and len(df_resources) > 0:
            st.write("**📅 Upload Activity Pattern**")
            
            df_resources['day_of_week'] = df_resources['dateUploaded'].dt.day_name()
            df_resources['week_of_year'] = df_resources['dateUploaded'].dt.isocalendar().week
            
            activity = df_resources.groupby(['week_of_year', 'day_of_week']).size().reset_index(name='count')
            
            # Create a pivot table for heatmap
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            if len(activity) > 0:
                fig_heatmap = px.density_heatmap(
                    activity,
                    x='week_of_year',
                    y='day_of_week',
                    z='count',
                    title='Resource Upload Activity (Week vs Day)',
                    labels={'week_of_year': 'Week of Year', 'day_of_week': 'Day of Week', 'count': 'Uploads'},
                    color_continuous_scale='YlOrRd',
                    category_orders={'day_of_week': day_order}
                )
                fig_heatmap.update_layout(height=350)
                st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Detailed Resource Table
        with st.expander("📋 View All Resources"):
            display_cols = ['name', 'type', 'dateUploaded', 'description']
            available_cols = [col for col in display_cols if col in df_resources.columns]
            
            if available_cols:
                display_df = df_resources[available_cols].copy()
                if 'dateUploaded' in display_df.columns:
                    display_df['dateUploaded'] = display_df['dateUploaded'].dt.strftime('%Y-%m-%d')
                
                st.dataframe(
                    display_df.rename(columns={
                        'name': 'Resource Name',
                        'type': 'Type',
                        'dateUploaded': 'Upload Date',
                        'description': 'Description'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No resources uploaded for this course yet")
else:
    st.info("Unable to load resource data")

st.write("---")

# ==============================================================================
# SECTION 4: TOPICS ANALYSIS
# ==============================================================================
st.subheader("📖 Course Topics")

if topics:
    df_topics = pd.DataFrame(topics)
    
    if not df_topics.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Topic list with visual representation
            st.write(f"**Total Topics in Course:** {len(df_topics)}")
            
            if 'name' in df_topics.columns:
                # Create a simple bar chart showing topics
                df_topics['topic_number'] = range(1, len(df_topics) + 1)
                
                fig_topics = px.bar(
                    df_topics,
                    y='name',
                    x='topic_number',
                    orientation='h',
                    title='Course Topics',
                    labels={'name': 'Topic', 'topic_number': 'Topic #'},
                    color='topic_number',
                    color_continuous_scale='teal'
                )
                fig_topics.update_layout(showlegend=False, height=max(300, len(df_topics) * 30))
                st.plotly_chart(fig_topics, use_container_width=True)
        
        with col2:
            # Topic statistics
            st.metric("Total Topics", len(df_topics))
            
            # Show topic IDs range
            if 'topicID' in df_topics.columns:
                st.write(f"**Topic ID Range:**")
                st.write(f"Min: {df_topics['topicID'].min()}")
                st.write(f"Max: {df_topics['topicID'].max()}")
        
        # Detailed Topic Table
        with st.expander("📋 View Topic Details"):
            st.dataframe(
                df_topics[['topicID', 'name']].rename(columns={
                    'topicID': 'Topic ID',
                    'name': 'Topic Name'
                }),
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No topics found for this course")
else:
    st.info("Unable to load topics for this course")

st.write("---")

# ==============================================================================
# SECTION 5: STUDY SESSIONS ANALYSIS
# ==============================================================================
st.subheader("🎓 Study Sessions Analysis")

study_sessions = make_api_call('GET', '/si/study_session')

if study_sessions:
    df_sessions = pd.DataFrame(study_sessions)
    
    if not df_sessions.empty:
        # Convert date columns
        if 'date' in df_sessions.columns:
            df_sessions['date'] = pd.to_datetime(df_sessions['date'])
        if 'startTime' in df_sessions.columns:
            df_sessions['startTime'] = pd.to_datetime(df_sessions['startTime'], format='%H:%M:%S', errors='coerce')
        if 'endTime' in df_sessions.columns:
            df_sessions['endTime'] = pd.to_datetime(df_sessions['endTime'], format='%H:%M:%S', errors='coerce')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Sessions", len(df_sessions))
        
        with col2:
            if 'building' in df_sessions.columns:
                unique_locations = df_sessions['building'].nunique()
                st.metric("Unique Locations", unique_locations)
        
        with col3:
            if 'date' in df_sessions.columns:
                upcoming = len(df_sessions[df_sessions['date'] >= pd.Timestamp.now()])
                st.metric("Upcoming Sessions", upcoming)
        
        st.write("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sessions by Location
            if 'building' in df_sessions.columns:
                location_counts = df_sessions['building'].value_counts().reset_index()
                location_counts.columns = ['building', 'count']
                
                fig_location = px.bar(
                    location_counts,
                    x='building',
                    y='count',
                    title='Study Sessions by Location',
                    labels={'building': 'Building', 'count': 'Number of Sessions'},
                    color='count',
                    color_continuous_scale='purples',
                    text='count'
                )
                fig_location.update_traces(textposition='outside')
                fig_location.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_location, use_container_width=True)
        
        with col2:
            # Sessions by Date (if available)
            if 'date' in df_sessions.columns:
                df_sessions['date_only'] = df_sessions['date'].dt.date
                date_counts = df_sessions.groupby('date_only').size().reset_index()
                date_counts.columns = ['date', 'count']
                
                fig_date = px.line(
                    date_counts,
                    x='date',
                    y='count',
                    title='Study Sessions Over Time',
                    labels={'date': 'Date', 'count': 'Number of Sessions'},
                    markers=True
                )
                fig_date.update_traces(line_color='#8B5CF6', line_width=3, marker=dict(size=8))
                fig_date.update_layout(height=400)
                st.plotly_chart(fig_date, use_container_width=True)
        
        # Session time distribution
        if 'startTime' in df_sessions.columns and df_sessions['startTime'].notna().any():
            st.write("**⏰ Session Start Time Distribution**")
            
            df_sessions['hour'] = df_sessions['startTime'].dt.hour
            hour_counts = df_sessions['hour'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['hour', 'count']
            hour_counts['hour_label'] = hour_counts['hour'].apply(lambda x: f"{x:02d}:00")
            
            fig_time = px.bar(
                hour_counts,
                x='hour_label',
                y='count',
                title='Sessions by Start Time',
                labels={'hour_label': 'Hour of Day', 'count': 'Number of Sessions'},
                color='count',
                color_continuous_scale='oranges'
            )
            fig_time.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Room capacity analysis
        if 'capacity' in df_sessions.columns and 'room' in df_sessions.columns:
            st.write("**🏢 Room Capacity Analysis**")
            
            room_capacity = df_sessions.groupby('room')['capacity'].first().reset_index()
            room_capacity = room_capacity.sort_values('capacity', ascending=False).head(10)
            
            fig_capacity = px.bar(
                room_capacity,
                x='room',
                y='capacity',
                title='Top 10 Rooms by Capacity',
                labels={'room': 'Room', 'capacity': 'Capacity'},
                color='capacity',
                color_continuous_scale='reds',
                text='capacity'
            )
            fig_capacity.update_traces(textposition='outside')
            fig_capacity.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_capacity, use_container_width=True)
        
        # Detailed Session Viewer
        st.write("---")
        st.write("**🔍 View Individual Session Details**")
        
        if 'sessionID' in df_sessions.columns:
            session_id = st.selectbox(
                "Select a session to view details:",
                df_sessions['sessionID'].tolist(),
                format_func=lambda x: f"Session {x}"
            )
            
            if st.button("Get Session Details", type="primary"):
                session_details = make_api_call('GET', f'/si/study_session/{session_id}')
                
                if session_details:
                    with st.expander(f"📋 Session {session_id} Details", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**📅 Date & Time:**")
                            if 'date' in session_details:
                                st.write(f"Date: {session_details['date']}")
                            if 'startTime' in session_details:
                                st.write(f"Start: {session_details['startTime']}")
                            if 'endTime' in session_details:
                                st.write(f"End: {session_details['endTime']}")
                            if 'durationMinutes' in session_details:
                                st.write(f"Duration: {session_details['durationMinutes']} min")
                        
                        with col2:
                            st.write("**📍 Location:**")
                            if 'building' in session_details:
                                st.write(f"Building: {session_details['building']}")
                            if 'room' in session_details:
                                st.write(f"Room: {session_details['room']}")
                            if 'capacity' in session_details:
                                st.write(f"Capacity: {session_details['capacity']}")
                        
                        with col3:
                            st.write("**📊 Statistics:**")
                            st.write(f"Session ID: {session_details.get('sessionID', 'N/A')}")
                        
                        # Show topics covered if available
                        if 'topics_covered' in session_details and session_details['topics_covered']:
                            st.write("---")
                            st.write("**📖 Topics Covered:**")
                            for topic in session_details['topics_covered']:
                                st.write(f"• {topic.get('topicName', 'Unknown')} ({topic.get('courseName', 'N/A')})")
                        else:
                            st.info("No topics recorded for this session")
    else:
        st.info("No study sessions available")
else:
    st.info("Unable to load study session data")

st.write("---")

# ==============================================================================
# SECTION 6: TEACHING ASSISTANT OVERVIEW
# ==============================================================================
st.subheader("👨‍🏫 Teaching Assistants")

if tas:
    df_tas = pd.DataFrame(tas)
    
    if not df_tas.empty:
        st.write(f"**TAs assigned to this course:** {len(df_tas)}")
        
        # Display TA cards
        cols = st.columns(min(3, len(df_tas)))
        for idx, ta in df_tas.iterrows():
            with cols[idx % 3]:
                with st.container():
                    st.write(f"**{ta.get('firstName', '')} {ta.get('lastName', '')}**")
                    st.write(f"📧 {ta.get('email', 'N/A')}")
                    if 'nuID' in ta:
                        st.caption(f"ID: {ta['nuID']}")
        
        # Detailed TA Table
        with st.expander("📋 View TA Details"):
            display_cols = ['firstName', 'lastName', 'email', 'nuID']
            available_cols = [col for col in display_cols if col in df_tas.columns]
            
            if available_cols:
                st.dataframe(
                    df_tas[available_cols].rename(columns={
                        'firstName': 'First Name',
                        'lastName': 'Last Name',
                        'email': 'Email',
                        'nuID': 'NU ID'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No TAs assigned to this course yet")
else:
    st.info("Unable to load TA data")

st.write("---")
st.caption("💡 **Dashboard Features:**")
st.caption("• Student enrollment distribution by year, section, and semester")
st.caption("• Resource type analysis and upload timeline")
st.caption("• Study session location and time patterns")
st.caption("• Course topics overview")
st.caption("• Teaching assistant assignments")