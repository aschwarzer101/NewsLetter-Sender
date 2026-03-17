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

# API_URL = "http://api:4000"


# # Call the SideBarLinks from the nav module in the modules directory
# SideBarLinks()

# # set the header of the page
# st.header('Course Materials Management')

# # You can access the session state to make a more customized/personalized app experience
# st.write(f"### Hi, {st.session_state['first_name']}.")

# # Select a course from the list of courses retrieved from the API
# courses = requests.get(f"{API_URL}/cr/course").json()
# selected_course = st.selectbox(
#     "Select a course:",
#     courses,
#     format_func=lambda x: f"{x['course_name']} CRN: {x['crn']}"
# )
# st.write(f"You selected: {selected_course['course_name']} (CRN: {selected_course['crn']})")

# # Upload a new course material (Professor - 2 user story)
# with st.expander("Upload New Course Material", expanded=False):
#     col1, col2 = st.columns(2)

#     with col1:
#         resource_name = st.text_input("Resource Name")
#         resource_type = st.selectbox("Resource Type", ["PDF", "Video", "Textbook", "URL", "Image", "Other"])

#     with col2:
#         resource_id = st.text_input("Resource ID")
#         upload_date = st.date_input("Upload Date")
    
#     description = st.text_area("Description")

#     if st.button("Upload Resource"):
#         data = {
#             "resourceID": resource_id,
#             "name": resource_name,
#             "type": resource_type,
#             "dateUploaded": str(upload_date),
#             "description": description,
#             "CRN": selected_course["crn"]   # FIXED KEY
#         }
#         response = requests.post(f"{API_URL}/cr/resources", json=data)

#         if response.status_code == 201:
#             st.success("Resource uploaded successfully!")
#         else:
#             st.error("Failed to upload resource.")
#             st.error(response.json())

# st.write("---")

# # Manage course materials (update/delete)
# st.subheader("Manage Existing Course Materials")
# resources = requests.get(f"{API_URL}/cr/resources/{selected_course['crn']}").json()

# for resource in resources:
#     with st.container():
#         col1, col2, col3 = st.columns([3, 1, 1])

#         with col1:
#             st.write(f"**{resource['name']}** ({resource['type']})")
#             st.caption(resource['description'] + f" | Uploaded on: {resource['dateUploaded']}")

#         # Update resource [Professor 1.4]
#         with col2:
#             if st.button("Edit", key=f"edit_{resource['resourceID']}"):
#                 st.session_state[f'editing_{resource["resourceID"]}'] = True

#         # Delete resource [Professor 1.3] -- FIXED INDENTATION
#         with col3:
#             if st.button("Delete", key=f"delete_{resource['resourceID']}"):
#                 response = requests.delete(f"{API_URL}/cr/resources/{resource['resourceID']}")
#                 if response.status_code == 200:
#                     st.success("Resource deleted successfully!")
#                 else:
#                     st.error("Failed to delete resource.")

#         # Edit form
#         if st.session_state.get(f'editing_{resource["resourceID"]}', False):
#             with st.form(key=f'form_{resource["resourceID"]}'):
#                 new_name = st.text_input("Resource Name", value=resource['name'])
#                 new_description = st.text_area("Description", value=resource['description'])

#                 colA, colB = st.columns(2)
#                 with colA:
#                     if st.form_submit_button("Save Changes"):
#                         update_data = {
#                             "name": new_name,
#                             "description": new_description
#                         }
#                         response = requests.put(f"{API_URL}/cr/resources/{resource['resourceID']}", json=update_data)
#                         if response.status_code == 200:
#                             st.success("Resource updated successfully!")
#                             st.session_state[f'editing_{resource["resourceID"]}'] = False

#                 with colB:
#                     if st.form_submit_button("Cancel"):
#                         st.session_state[f'editing_{resource["resourceID"]}'] = False

#         st.divider()


import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
from streamlit_extras.app_logo import add_logo
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks
import requests 

# Use correct hostname from docker-compose.yml
API_URL = "http://web-api:4000"

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.header('📚 Course Materials Management')

# You can access the session state to make a more customized/personalized app experience
st.write(f"### Hi, {st.session_state['first_name']}.")

# Helper function for API calls with error handling
def make_api_call(method, endpoint, **kwargs):
    """Make API call with proper error handling"""
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.request(method, url, timeout=5, **kwargs)
        
        # Check if response is successful
        if response.status_code >= 400:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
            
        # Try to parse JSON
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            st.error(f"Invalid JSON response from {endpoint}")
            st.write("Response text:", response.text[:200])
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Please check if the API container is running.")
        st.write("**Troubleshooting:**")
        st.code("docker-compose ps")
        st.code("docker-compose logs api")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# Test API connection first
with st.spinner("Connecting to API..."):
    test_response = make_api_call('GET', '/cr/course')

if test_response is None:
    st.stop()

courses = test_response

if not courses:
    st.warning("No courses found. Please create a course first.")
    if st.button("➕ Go to Create Course Page"):
        st.switch_page('pages/03_Professor_Manage_Courses.py')
    st.stop()

# Select a course from the list of courses retrieved from the API
selected_course = st.selectbox(
    "Select a course:",
    courses,
    format_func=lambda x: f"{x.get('name', 'Unknown')} (CRN: {x.get('CRN', 'N/A')})"
)

if selected_course:
    st.write(f"You selected: **{selected_course.get('name', 'Unknown')}** (CRN: {selected_course.get('CRN', 'N/A')})")

    st.write("---")

    # Upload a new course material (Professor User Story 1.2 - POST)
    with st.expander("➕ Upload New Course Material", expanded=False):
        with st.form("upload_form"):
            col1, col2 = st.columns(2)

            with col1:
                resource_name = st.text_input("Resource Name*")
                resource_type = st.selectbox("Resource Type*", ["PDF", "Video", "Slides", "Document", "Textbook", "URL", "Image", "Other"])

            with col2:
                resource_id = st.number_input("Resource ID*", min_value=1, value=5001)
                upload_date = st.date_input("Upload Date*")
            
            description = st.text_area("Description*")

            submitted = st.form_submit_button("Upload Resource", type="primary", use_container_width=True)
            
            if submitted:
                if not resource_name or not description:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    data = {
                        "resourceID": int(resource_id),
                        "name": resource_name,
                        "type": resource_type,
                        "dateUploaded": str(upload_date),
                        "description": description,
                        "CRN": selected_course["CRN"]
                    }
                    
                    result = make_api_call('POST', '/cr/resources', json=data)
                    
                    if result:
                        st.success("✅ Resource uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to upload resource. Check error above.")

    st.write("---")

    # Manage course materials (update/delete) - Professor User Stories 1.3 & 1.4
    st.subheader("Existing Course Materials")
    
    # Get resources for the selected course
    resources = make_api_call('GET', f'/cr/resources?crn={selected_course["CRN"]}')

    if resources is None:
        st.error("Could not load resources. Check API connection.")
    elif not resources:
        st.info("📝 No resources uploaded yet for this course. Use the form above to upload your first resource!")
    else:
        st.write(f"Total resources: **{len(resources)}**")
        st.write("")
        
        for resource in resources:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"**{resource.get('name', 'Unnamed')}** ({resource.get('type', 'Unknown')})")
                    desc = resource.get('description', 'No description')
                    date = resource.get('dateUploaded', 'Unknown date')
                    st.caption(f"{desc} | Uploaded on: {date}")

                # Update resource [Professor User Story 1.4 - PUT]
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{resource['resourceID']}", use_container_width=True):
                        st.session_state[f'editing_{resource["resourceID"]}'] = True

                # Delete resource [Professor User Story 1.3 - DELETE]
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{resource['resourceID']}", type="secondary", use_container_width=True):
                        result = make_api_call('DELETE', f'/cr/resources/{resource["resourceID"]}')
                        if result is not None:
                            st.success("✅ Resource deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete resource.")

                # Edit form
                if st.session_state.get(f'editing_{resource["resourceID"]}', False):
                    with st.form(key=f'form_{resource["resourceID"]}'):
                        st.write("**Edit Resource**")
                        
                        new_name = st.text_input("Resource Name", value=resource.get('name', ''))
                        new_type = st.selectbox(
                            "Type", 
                            ["PDF", "Video", "Slides", "Document", "Textbook", "URL", "Image", "Other"],
                            index=0 if resource.get('type') not in ["PDF", "Video", "Slides", "Document", "Textbook", "URL", "Image", "Other"] 
                            else ["PDF", "Video", "Slides", "Document", "Textbook", "URL", "Image", "Other"].index(resource.get('type'))
                        )
                        new_description = st.text_area("Description", value=resource.get('description', ''))

                        colA, colB = st.columns(2)
                        with colA:
                            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                                if not new_name or not new_description:
                                    st.error("Name and description cannot be empty")
                                else:
                                    update_data = {
                                        "name": new_name,
                                        "type": new_type,
                                        "description": new_description
                                    }
                                    result = make_api_call('PUT', f'/cr/resources/{resource["resourceID"]}', json=update_data)
                                    if result is not None:
                                        st.success("✅ Resource updated successfully!")
                                        st.session_state[f'editing_{resource["resourceID"]}'] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update resource.")

                        with colB:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f'editing_{resource["resourceID"]}'] = False
                                st.rerun()

                st.divider()

# Footer with helpful info
st.write("---")
st.caption("💡 **Tips:**")
st.caption("• Click 'Upload New Course Material' to add resources (User Story 1.2)")
st.caption("• Click 'Edit' to modify resource details (User Story 1.4)")
st.caption("• Click 'Delete' to remove outdated materials (User Story 1.3)")
