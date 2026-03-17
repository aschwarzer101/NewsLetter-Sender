# import streamlit as st
# import requests

# st.title("Manage Courses")

# tab1, tab2 = st.tabs(["Create New Course", "View/Edit Courses"])

# with tab1:
#     st.subheader("Create New Course")
    
#     # Create new course [Professor-5]
#     with st.form("create_course_form"):
#         col1, col2 = st.columns(2)
        
#         with col1:
#             crn = st.number_input("CRN")
#             course_num = st.number_input("Course Number")
        
#         with col2:
#             course_name = st.text_input("Course Name")
#             department = st.text_input("Department")
        
#         submitted = st.form_submit_button("Create Course")
        
#         if submitted:
#             data = {
#                 "CRN": crn,
#                 "courseNum": course_num,
#                 "name": course_name,
#                 "department": department
#             }
            
#             response = requests.post('http://api:4000/cr/courses', json=data)
            
#             if response.status_code == 201:
#                 st.success(f"Course '{course_name}' created successfully!")
#             else:
#                 st.error(f"Error: {response.json()}")

# with tab2:
#     st.subheader("Your Courses")
    
#     # Get all courses for this professor
#     courses = requests.get(f'http://api:4000/c/professor/{st.session_state["ProfessorID"]}/courses').json()
    
#     for course in courses:
#         with st.expander(f"{course['name']} - CRN: {course['CRN']}"):
#             # Get course details (GET /course/<crn>)
#             details = requests.get(f'http://api:4000/c/course/{course["CRN"]}').json()
            
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.write(f"**Department:** {details['department']}")
#                 st.write(f"**Course Number:** {details['courseNum']}")
#             with col2:
#                 st.write(f"**CRN:** {details['CRN']}")
            
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 if st.button("View Materials", key=f"mat_{course['CRN']}"):
#                     st.session_state['selected_crn'] = course['CRN']
#                     st.switch_page('pages/Professor_Course_Materials.py')
#             with col2:
#                 if st.button("View Analytics", key=f"ana_{course['CRN']}"):
#                     st.session_state['selected_crn'] = course['CRN']
#                     st.switch_page('pages/Professor_Student_Analytics.py')


import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("🎓 Manage Courses")
st.write(f"### Hi, {st.session_state.get('first_name', 'Professor')}.")

# Helper function for API calls
def make_api_call(method, endpoint, **kwargs):
    """Make API call with proper error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.request(method, url, timeout=5, **kwargs)
        
        if response.status_code >= 400:
            return {"error": True, "status": response.status_code, "message": response.text}
            
        try:
            return {"error": False, "data": response.json(), "status": response.status_code}
        except requests.exceptions.JSONDecodeError:
            return {"error": True, "message": "Invalid JSON response"}
            
    except requests.exceptions.ConnectionError:
        return {"error": True, "message": "Cannot connect to API"}
    except Exception as e:
        return {"error": True, "message": str(e)}

tab1, tab2 = st.tabs(["➕ Create New Course", "📚 View/Manage Courses"])

# ==============================================================================
# TAB 1: CREATE NEW COURSE
# ==============================================================================
with tab1:
    st.subheader("Create New Course")
    st.write("Fill in the details below to create a new course.")
    
    with st.form("create_course_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            crn = st.number_input("CRN*", min_value=10000, max_value=99999, value=12345, help="5-digit Course Reference Number")
            course_num = st.number_input("Course Number*", min_value=1000, max_value=9999, value=3200, help="4-digit course number")
        
        with col2:
            course_name = st.text_input("Course Name*", value="Database Design", help="Full name of the course")
            department = st.selectbox(
                "Department*",
                [
                    "Computer Science",
                    "Mathematics", 
                    "Economics",
                    "Biology",
                    "Physics",
                    "Chemistry",
                    "Engineering",
                    "Business",
                    "English",
                    "History",
                    "Psychology",
                    "Political Science"
                ],
                help="Academic department offering the course"
            )
        
        st.write("")
        st.caption("* Required fields")
        
        submitted = st.form_submit_button("Create Course", type="primary", use_container_width=True)
        
        if submitted:
            if not course_name:
                st.error("❌ Course name is required")
            else:
                data = {
                    "CRN": int(crn),
                    "courseNum": int(course_num),
                    "name": course_name,
                    "department": department
                }
                
                # POST to /cr/course (NOT /cr/courses)
                result = make_api_call('POST', '/cr/course', json=data)
                
                if not result['error']:
                    st.success(f"✅ Course '{course_name}' created successfully!")
                    st.balloons()
                    
                    # Display created course details
                    with st.container():
                        st.write("**Course Details:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**CRN:** {crn}")
                        with col2:
                            st.write(f"**Course:** {department} {course_num}")
                        with col3:
                            st.write(f"**Name:** {course_name}")
                else:
                    st.error(f"❌ Error creating course: {result.get('message', 'Unknown error')}")
                    
                    # Provide helpful error messages
                    if result.get('status') == 500:
                        st.warning("💡 **Tip:** This might be a duplicate CRN. Try a different CRN number.")
                    elif 'Duplicate' in str(result.get('message', '')):
                        st.warning("💡 **Tip:** A course with this CRN already exists. Use a unique CRN.")

# ==============================================================================
# TAB 2: VIEW/MANAGE COURSES
# ==============================================================================
with tab2:
    st.subheader("Your Courses")
    
    # Get professor ID from session state
    prof_id = st.session_state.get('prof_id', 1001)
    
    # Option 1: Try to get professor-specific courses (if route exists)
    # Option 2: Get all courses and filter (fallback)
    
    # First, try to get all courses
    result = make_api_call('GET', '/cr/course')
    
    if result['error']:
        st.error(f"❌ Error loading courses: {result.get('message', 'Unknown error')}")
        st.write("**Troubleshooting:**")
        st.write("1. Check if the API container is running: `docker-compose ps`")
        st.write("2. Check API logs: `docker-compose logs api`")
        st.write("3. Verify database connection")
    else:
        courses = result['data']
        
        if courses and len(courses) > 0:
            # Add filter options
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Total Courses:** {len(courses)}")
            
            with col2:
                # Department filter
                all_departments = list(set([c.get('department', 'Unknown') for c in courses]))
                selected_dept = st.selectbox(
                    "Filter by Department:",
                    ["All Departments"] + sorted(all_departments)
                )
            
            # Filter courses if needed
            if selected_dept != "All Departments":
                courses = [c for c in courses if c.get('department') == selected_dept]
            
            st.write("")
            
            # Display each course
            for course in courses:
                with st.expander(
                    f"{course.get('department', 'Unknown')} {course.get('courseNum', '')} - "
                    f"{course.get('name', 'Unnamed')} (CRN: {course.get('CRN', 'N/A')})"
                ):
                    # Get detailed course info
                    details_result = make_api_call('GET', f'/cr/course/{course.get("CRN")}')
                    
                    if not details_result['error']:
                        details = details_result['data']
                        
                        # Display course details
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**📚 Course Information**")
                            st.write(f"Department: {details.get('department', 'N/A')}")
                            st.write(f"Course Number: {details.get('courseNum', 'N/A')}")
                        
                        with col2:
                            st.write("**🔢 Identifiers**")
                            st.write(f"CRN: {details.get('CRN', 'N/A')}")
                        
                        with col3:
                            st.write("**📊 Quick Stats**")
                            
                            # Get resource count
                            resources_result = make_api_call('GET', f'/cr/resources?crn={course.get("CRN")}')
                            if not resources_result['error']:
                                resource_count = len(resources_result['data'])
                                st.write(f"Resources: {resource_count}")
                            
                            # Get topic count
                            topics_result = make_api_call('GET', f'/cr/topic?crn={course.get("CRN")}')
                            if not topics_result['error']:
                                topic_count = len(topics_result['data'])
                                st.write(f"Topics: {topic_count}")
                            
                            # Get enrollment count
                            enrollments_result = make_api_call('GET', f'/cr/course/{course.get("CRN")}/enrollments')
                            if not enrollments_result['error']:
                                student_count = len(enrollments_result['data'])
                                st.write(f"Students: {student_count}")
                    
                    st.write("---")
                    st.write("**Quick Actions:**")
                    
                    # Quick action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(
                            "📚 View Materials", 
                            key=f"mat_{course.get('CRN')}", 
                            use_container_width=True,
                            type="primary"
                        ):
                            st.session_state['selected_crn'] = course.get('CRN')
                            st.switch_page('pages/01_Professor_Course_Materials.py')
                    
                    with col2:
                        if st.button(
                            "📊 View Analytics", 
                            key=f"ana_{course.get('CRN')}", 
                            use_container_width=True
                        ):
                            st.session_state['selected_crn'] = course.get('CRN')
                            st.switch_page('pages/02_Professor_Student_Analytics.py')
                    
                    with col3:
                        if st.button(
                            "👥 View Students", 
                            key=f"stu_{course.get('CRN')}", 
                            use_container_width=True
                        ):
                            # Show students in expander
                            enrollments_result = make_api_call('GET', f'/cr/course/{course.get("CRN")}/enrollments')
                            if not enrollments_result['error'] and enrollments_result['data']:
                                st.write("**Enrolled Students:**")
                                for student in enrollments_result['data']:
                                    st.write(f"• {student.get('firstName', '')} {student.get('lastName', '')} ({student.get('email', '')})")
                            else:
                                st.info("No students enrolled yet")
        else:
            st.info("📝 No courses found. Create your first course using the tab above!")
            
            # Helpful tips
            st.write("**Getting Started:**")
            st.write("1. Click on the 'Create New Course' tab above")
            st.write("2. Fill in the course details")
            st.write("3. Click 'Create Course' to add it to the system")

st.write("---")
st.caption("💡 **User Story Covered:**")
st.caption("• 1.5: Create a new course (POST /cr/course)")
st.caption("• View all courses (GET /cr/course)")
st.caption("• View course details (GET /cr/course/{crn})")