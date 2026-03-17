import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout='wide')

SideBarLinks()

st.title('🎓 Course Search')

st.write("## Browse All Courses")

if st.button("Load All Courses", type="primary", use_container_width=True):
    try:
        url = "http://web-api:4000/courses"
        response = requests.get(url)
        
        if response.status_code == 200:
            courses = response.json()
            
            if courses and len(courses) > 0:
                st.success(f"Found {len(courses)} courses!")
                df = pd.DataFrame(courses)
                df.columns = ['CRN', 'Department', 'Course #', 'Course Name']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("No courses found.")
        else:
            st.error("Could not load courses")
    except Exception as e:
        st.error(f"Error: {e}")

st.write("---")

st.write("## 🔍 Search Courses")

search_option = st.radio("Search by:", ["Department", "Course Number", "CRN", "Keyword"], horizontal=True)

if search_option == "Department":
    department = st.selectbox("Select department:", 
                             ["Computer Science", "Data Science", "Mathematics"])
    
    if st.button("Search", use_container_width=True):
        try:
            url = f"http://web-api:4000/courses/department?department={department}"
            response = requests.get(url)
            
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    st.success(f"Found {len(courses)} courses!")
                    df = pd.DataFrame(courses)
                    df.columns = ['CRN', 'Department', 'Course #', 'Course Name']
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No courses found.")
        except Exception as e:
            st.error(f"Error: {e}")

elif search_option == "Course Number":
    col1, col2 = st.columns(2)
    with col1:
        dept = st.selectbox("Department:", ["Computer Science", "Data Science", "Mathematics"])
    with col2:
        course_num_input = st.text_input("Course Number:", value="3200", max_chars=4)  # ✅ Changed
    
    if st.button("Search", use_container_width=True):
        try:
            course_num = int(course_num_input)  # Convert to integer
            url = f"http://web-api:4000/courses/search?department={dept}&courseNum={course_num}"
            response = requests.get(url)
            
            if response.status_code == 200:
                courses = response.json()
                if courses:
                    st.success("Course found!")
                    for course in courses:
                        st.write(f"**{course['department']} {course['courseNum']} - {course['name']}**")
                        st.write(f"CRN: {course['crn']}")
                else:
                    st.info("Course not found.")
        except ValueError:
            st.error("Please enter a valid course number")
        except Exception as e:
            st.error(f"Error: {e}")

elif search_option == "CRN":
    crn_input = st.text_input("Enter CRN:", value="12345", max_chars=5)  # ✅ Changed
    
    if st.button("Get Details", use_container_width=True):
        try:
            crn = int(crn_input)  # Convert to integer
            url = f"http://web-api:4000/courses/{crn}"
            response = requests.get(url)
            
            if response.status_code == 200:
                course = response.json()
                
                if course and 'crn' in course:
                    st.success("Course found!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Course Information:**")
                        st.write(f"**{course['department']} {course['courseNum']}**")
                        st.write(f"**{course['name']}**")
                        st.write(f"CRN: {course['crn']}")
                    
                    with col2:
                        # Get professors
                        try:
                            prof_url = f"http://web-api:4000/courses/{crn}/professors"
                            prof_response = requests.get(prof_url)
                            
                            if prof_response.status_code == 200:
                                professors = prof_response.json()
                                if professors:
                                    st.write("**Professors:**")
                                    for prof in professors:
                                        st.write(f"• {prof.get('firstName', '')} {prof.get('lastName', '')}")
                        except:
                            pass
                    
                    st.write("---")
                    
                    # Get topics
                    try:
                        topics_url = f"http://web-api:4000/courses/{crn}/topics"
                        topics_response = requests.get(topics_url)
                        
                        if topics_response.status_code == 200:
                            topics = topics_response.json()
                            if topics:
                                st.write("**📚 Topics Covered:**")
                                for topic in topics:
                                    st.write(f"• {topic.get('name', 'Unknown')}")
                    except:
                        pass
                else:
                    st.warning("Course not found.")
            else:
                st.error("Course not found.")
        except ValueError:
            st.error("Please enter a valid CRN number")
        except Exception as e:
            st.error(f"Error: {e}")

else:  # Keyword
    keyword = st.text_input("Enter keyword:", "")
    
    if st.button("Search", use_container_width=True):
        if keyword.strip():
            try:
                url = f"http://web-api:4000/courses/search/keyword?keyword={keyword}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    courses = response.json()
                    if courses:
                        st.success(f"Found {len(courses)} courses!")
                        df = pd.DataFrame(courses)
                        df.columns = ['CRN', 'Department', 'Course #', 'Course Name']
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No courses found.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a keyword")

st.write("---")