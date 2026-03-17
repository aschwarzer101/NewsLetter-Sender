import pandas as pd
import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
st.markdown("""
    <style>
        /* Tab container background */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f0f2f6;  /* change this */
            border-radius: 8px;
            padding: 6px;
        }

        /* Individual tab background */
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff; /* normal tab */
            border-radius: 6px;
            padding: 4px 12px;
        }

        /* Active (selected) tab background */
        .stTabs [aria-selected="true"] {
            background-color: #d9eaff !important; /* selected tab */
            color: black !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Student & TA Management",
    layout="wide"
)

# Initialize sidebar
SideBarLinks()

st.title("Student & TA Management")
st.markdown("---")

# API endpoint

API_URL = "http://api:4000"
st.markdown("Select management group:")
#larger tabs between student management and TA management
st.markdown('<div class="special-tabs">', unsafe_allow_html=True)
admin_tab1, admin_tab2 = st.tabs(["Student Management", "TA Team Management"])

st.markdown("---")
with admin_tab1: 

    st.header("Student Management")
    st.markdown("---")

    student_tab1, student_tab2, student_tab3 = st.tabs(["View Students", "Add Student", "Update/Remove Student"])

    # -- View students tab ---
    with student_tab1:
        st.subheader("Current Students")
        
        if st.button("Refresh Student List", key="refresh_students"):
            try:
                response = requests.get(f"{API_URL}/sm/students")
                if response.status_code == 200:
                    students = response.json()
                    if students:
                        df = pd.DataFrame(students)
                        # Display as table
                        st.dataframe(
                            df[['nuID', 'firstName', 'lastName', 'email', 'majorOne', 'classYear']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No students found")
                else:
                    st.error(f"Error fetching students: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    # ---------- TAB 2: Add Student ----------
    with student_tab2:
        st.subheader("Add New Student")
        
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_nuid = st.text_input("NU ID", placeholder="002345678")
                new_first = st.text_input("First Name")
                new_last = st.text_input("Last Name")
                new_email = st.text_input("Email", placeholder="student@northeastern.edu")
            
            with col2:
                new_grad_year = st.date_input("Graduation Year")
                new_major1 = st.selectbox("Major", 
                    ["Computer Science", "Data Science", "Mathematics", "Business", "Other"])
                new_major2 = st.selectbox("Second Major (Optional)", 
                    ["None", "Computer Science", "Data Science", "Mathematics", "Business"])
                new_minor = st.selectbox("Minor (Optional)",
                    ["None", "Business Administration", "Statistics", "Mathematics"])
            
            submitted = st.form_submit_button("Add Student")
            
            if submitted:
                # Prepare data
                student_data = {
                    "nuID": int(new_nuid) if new_nuid else None,
                    "firstName": new_first,
                    "lastName": new_last,
                    "email": new_email,
                    "gradYear": str(new_grad_year),
                    "majorOne": new_major1,
                    "majorTwo": new_major2 if new_major2 != "None" else None,
                    "minor": new_minor if new_minor != "None" else None
                }
                
                try:
                    response = requests.post(f"{API_URL}/sm/students", json=student_data)  # ← Fixed!
                    if response.status_code == 201:
                        st.success(f"✅ Student {new_first} {new_last} added successfully!")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    # ---------- TAB 3: Manage Students ----------
    with student_tab3:
        st.subheader("Update or Remove Students")
        
        # Student selector
        student_nuid = st.text_input("Enter Student NU ID", placeholder="002345678", key="manage_nuid")
        
        # Look up student button
        if student_nuid and st.button("🔍 Look Up Student", key="lookup_student"):
            try:
                response = requests.get(f"{API_URL}/sm/student/{student_nuid}")
                if response.status_code == 200:
                    student = response.json()
                    st.success(f"Found: {student['firstName']} {student['lastName']}")
                    
                    # Display student info in a nice format
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {student['firstName']} {student['lastName']}")
                        st.write(f"**Email:** {student['email']}")
                        st.write(f"**Major:** {student['majorOne']}")
                    with col2:
                        st.write(f"**Class Year:** {student['classYear']}")
                        st.write(f"**Grad Year:** {student['gradYear']}")
                        if student.get('minor'):
                            st.write(f"**Minor:** {student['minor']}")
                else:
                    st.error("Student not found")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        # Three columns for different actions
        col1, col2, col3 = st.columns(3)
        
        # -------- Column 1: Update Student Info --------
        with col1:
            st.markdown("#### ✏️ Update Student Info")
            
            with st.form("update_student_form"):
                update_email = st.text_input("New Email", key="update_email")
                update_major = st.selectbox("Update Major", 
                    ["", "Computer Science", "Data Science", "Mathematics", "Business"], key="update_major")
                update_minor = st.selectbox("Update Minor",
                    ["", "None", "Business Administration", "Statistics", "Mathematics"], key="update_minor")
                
                update_submitted = st.form_submit_button("💾 Update Info")
                
                if update_submitted:
                    if student_nuid:
                        update_data = {}
                        if update_email:
                            update_data["email"] = update_email
                        if update_major:
                            update_data["majorOne"] = update_major
                        if update_minor and update_minor != "":
                            update_data["minor"] = update_minor if update_minor != "None" else None
                        
                        if update_data:
                            try:
                                response = requests.put(f"{API_URL}/sm/student/{student_nuid}", json=update_data)
                                if response.status_code == 200:
                                    st.success("✅ Student updated successfully!")
                                else:
                                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Connection error: {str(e)}")
                        else:
                            st.warning("No fields to update")
                    else:
                        st.warning("Please enter a student NU ID")
        
        # -------- Column 2: Convert to Peer Tutor --------
        with col2:
            st.markdown("#### 🎓 Convert to Peer Tutor")
            st.info("Promote a student to become a peer tutor")
            
            if st.button("✨ Convert to Peer Tutor", key="convert_tutor", use_container_width=True):
                if student_nuid:
                    try:
                        response = requests.post(f"{API_URL}/sm/peer_tutors/{student_nuid}")
                        if response.status_code == 201:
                            st.success("✅ Student converted to peer tutor!")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a student NU ID first")
        
        # -------- Column 3: Remove Student --------
        with col3:
            st.markdown("####  Remove Student")
            st.warning("⚠️ Permanently removes student from course")
            
            confirm_delete = st.checkbox("I confirm deletion", key="confirm_delete")
            
            if st.button("🗑️ Remove Student", key="delete_student", type="secondary", use_container_width=True, disabled=not confirm_delete):
                if student_nuid:
                    try:
                        response = requests.delete(f"{API_URL}/sm/students/{student_nuid}")
                        if response.status_code == 200:
                            st.success("✅ Student removed successfully!")
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a student NU ID first")

    st.markdown("---")


# TEACHING ASSISTANT MANAGEMENT SECTION===============================================

with admin_tab2: 
    st.header("👨‍🏫 Teaching Assistant Management")

    ta_tab1, ta_tab2 = st.tabs(["View TAs", "Add TA"])

    # ---------- TAB 1: View TAs ----------
    with ta_tab1:
        st.subheader("Current Teaching Assistants")
        
        # Optional filter by course
        col1, col2 = st.columns([3, 1])
        with col1:
            filter_crn = st.text_input("Filter by Course CRN (Optional)", placeholder="12345", key="filter_ta_crn")
        with col2:
            st.write("")  # Spacing
            refresh_tas = st.button("🔄 Refresh", key="refresh_tas", use_container_width=True)
        
        if refresh_tas:
            try:
                url = f"{API_URL}/pa/teaching_assistants"
                if filter_crn:
                    url += f"?crn={filter_crn}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    tas = response.json()
                    if tas:
                        df = pd.DataFrame(tas)
                        st.dataframe(
                            df[['nuID', 'firstName', 'lastName', 'email', 'crn']],
                            use_container_width=True,
                            hide_index=True
                        )
                        st.success(f"✅ Showing {len(tas)} teaching assistant(s)")
                    else:
                        st.info("No TAs found")
                else:
                    st.error(f"Error fetching TAs: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    # ---------- TAB 2: Add TA ----------
    with ta_tab2:
        st.subheader("Add New Teaching Assistant to Team")
        
        with st.form("add_ta_form"):
            st.markdown("**TA Information**")
            col1, col2 = st.columns(2)
            
            with col1:
                ta_nuid = st.text_input("NU ID *", placeholder="001567890")
                ta_first = st.text_input("First Name *")
                ta_last = st.text_input("Last Name *")
            
            with col2:
                ta_email = st.text_input("Email *", placeholder="ta@northeastern.edu")
                ta_crn = st.number_input("Course CRN *", min_value=10000, max_value=99999, value=12345, step=1)
                ta_admin_id = st.number_input("Your Admin NU ID *", min_value=1000000, max_value=9999999, value=1234567, step=1)
            
            st.markdown("*Required fields")
            submitted = st.form_submit_button("➕ Add Teaching Assistant", type="primary")
            
            if submitted:
                if not ta_nuid or not ta_first or not ta_last or not ta_email:
                    st.error("⚠️ Please fill in all required fields")
                else:
                    ta_data = {
                        "nuID": int(ta_nuid),
                        "firstName": ta_first,
                        "lastName": ta_last,
                        "email": ta_email,
                        "crn": ta_crn,
                        "adminID": ta_admin_id
                    }
                    
                    try:
                        response = requests.post(f"{API_URL}/pa/teaching_assistants", json=ta_data)
                        if response.status_code == 201:
                            st.success(f"✅ TA {ta_first} {ta_last} added to the team!")
                            st.balloons()
                        else:
                            st.error(f":material.close: Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")

