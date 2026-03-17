import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Course Resources",
    page_icon=":material/book:",
    layout="wide"
)

SideBarLinks()

st.title(":material/book: Course Resources")
st.markdown("View and manage study materials for courses you tutor")
st.markdown("---")

API_URL = "http://api:4000"

# DASHBOARD METRICS
col1, col2, col3 = st.columns(3)

try:
    # Total resources
    all_resources = requests.get(f"{API_URL}/cr/resources")
    total_resources = len(all_resources.json()) if all_resources.status_code == 200 else 0
    
    # PDF resources
    pdf_resources = requests.get(f"{API_URL}/cr/resources?type=PDF")
    pdf_count = len(pdf_resources.json()) if pdf_resources.status_code == 200 else 0
    
    # Video resources
    video_resources = requests.get(f"{API_URL}/cr/resources?type=Video")
    video_count = len(video_resources.json()) if video_resources.status_code == 200 else 0
    
    with col1:
        st.metric(
            label=":material/folder: Total Resources",
            value=total_resources,
            delta=None
        )
    
    with col2:
        st.metric(
            label=":material/description: PDFs",
            value=pdf_count,
            delta=None
        )
    
    with col3:
        st.metric(
            label=":material/video_library: Videos",
            value=video_count,
            delta=None
        )

except Exception as e:
    st.error(f"Error loading metrics: {str(e)}")

st.markdown("---")

# TABS FOR DIFFERENT ACTIONS
resource_tab1, resource_tab2, resource_tab3 = st.tabs([
    ":material/menu_book: Browse Resources", 
    ":material/upload: Upload Resource", 
    ":material/edit: Manage My Resources"
])

# ========== TAB 1: Browse Resources ==========
with resource_tab1:
    st.subheader("Browse Course Materials")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filter_crn = st.text_input(
            "Filter by Course CRN",
            placeholder="12345",
            key="browse_crn"
        )
    
    with col2:
        filter_type = st.selectbox(
            "Filter by Type",
            ["All Types", "PDF", "Video", "Textbook", "URL", "Image", "Other"],
            key="browse_type"
        )
    
    with col3:
        st.write("")  # Spacing
        search_btn = st.button(
            ":material/search: Search",
            key="search_resources",
            use_container_width=True
        )
    
    if search_btn or 'browse_first_load' not in st.session_state:
        st.session_state.browse_first_load = True
        
        try:
            url = f"{API_URL}/cr/resources"
            params = []
            
            if filter_crn:
                params.append(f"crn={filter_crn}")
            if filter_type != "All Types":
                params.append(f"type={filter_type}")
            
            if params:
                url += "?" + "&".join(params)
            
            response = requests.get(url)
            
            if response.status_code == 200:
                resources = response.json()
                
                if resources:
                    for resource in resources:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([3, 2, 1])
                            
                            with col1:
                                st.markdown(f"### {resource['name']}")
                                if resource.get('description'):
                                    st.caption(resource['description'])
                                st.caption(f":material/calendar_today: Uploaded: {resource['dateUploaded']}")
                            
                            with col2:
                                # Resource type badge
                                type_colors = {
                                    'PDF': 'blue',
                                    'Video': 'red',
                                    'Textbook': 'green',
                                    'URL': 'violet',
                                    'Image': 'orange',
                                    'Other': 'gray'
                                }
                                color = type_colors.get(resource['type'], 'gray')
                                st.badge(resource['type'], color=color, width="content")
                                
                                if resource.get('CRN'):
                                    st.write(f"**Course:** {resource['CRN']}")
                            
                            with col3:
                                st.write(f"**ID:** {resource['resourceID']}")
                    
                    st.success(f":material/check_circle: Showing {len(resources)} resource(s)")
                else:
                    st.info("No resources found matching your filters")
            else:
                st.error(f"Error fetching resources: {response.text}")
        
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

# ========== TAB 2: Upload Resource ==========
with resource_tab2:
    st.subheader("Upload Study Material")
    st.info(":material/lightbulb: Share helpful resources you used when taking this course")
    
    with st.form("upload_resource_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            resource_name = st.text_input(
                "Resource Name *",
                placeholder="Exam Study Guide",
                key="upload_name"
            )
            resource_type = st.selectbox(
                "Type *",
                ["PDF", "Video", "Textbook", "URL", "Image", "Other"],
                key="upload_type"
            )
            resource_crn = st.number_input(
                "Course CRN *",
                min_value=10000,
                max_value=99999,
                value=12345,
                step=1,
            )
        
        with col2:
            resource_description = st.text_area(
                "Description",
                placeholder="Brief description of the resource and how it helped you...",
                key="upload_desc",
                height=150
            )
        
        st.markdown("*Required fields")
        upload_submitted = st.form_submit_button(
            ":material/upload: Upload Resource",
            type="primary",
            use_container_width=True
        )
        
        if upload_submitted:
            if not resource_name:
                st.error(":material/warning: Please enter a resource name")
            else:
                resource_data = {
                    "name": resource_name,
                    "type": resource_type,
                    "dateUploaded": str(date.today()),
                    "description": resource_description if resource_description else None,
                    "CRN": resource_crn
                }
                
                try:
                    response = requests.post(
                        f"{API_URL}/cr/resources",
                        json=resource_data
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.success(f":material/check_circle: Resource '{resource_name}' uploaded successfully!")
                        st.balloons()
                    else:
                        # Try to parse error message
                        try:
                            error_msg = response.json().get('error', 'Unknown error')
                        except:
                            error_msg = response.text
                        st.error(f"Error: {error_msg}")
                except requests.exceptions.JSONDecodeError as e:
                    st.error(f"JSON Decode Error: {str(e)}")
                    st.error(f"Response text: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

# ========== TAB 3: Manage My Resources ==========
with resource_tab3:
    st.subheader("Edit or Remove Resources")
    
    # Resource lookup
    resource_id_manage = st.number_input(
        "Enter Resource ID to Manage",
        min_value=5001,
        max_value=99999,
        value=5001,
        step=1,
        key="manage_resource_id"
    )
    
    if st.button(":material/search: Look Up Resource", key="lookup_resource"):
        try:
            response = requests.get(f"{API_URL}/cr/resources")
            if response.status_code == 200:
                all_resources = response.json()
                resource = next(
                    (r for r in all_resources if r['resourceID'] == resource_id_manage),
                    None
                )
                
                if resource:
                    st.success(f"Found: {resource['name']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {resource['name']}")
                        st.write(f"**Type:** {resource['type']}")
                        st.write(f"**CRN:** {resource.get('CRN', 'N/A')}")
                    with col2:
                        st.write(f"**Uploaded:** {resource['dateUploaded']}")
                        st.write(f"**Description:** {resource.get('description', 'N/A')}")
                else:
                    st.error("Resource not found")
            else:
                st.error("Error fetching resources")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Edit and Delete columns
    col1, col2 = st.columns(2)
    
    # -------- Edit Resource --------
    with col1:
        st.markdown("#### :material/edit: Edit Resource")
        
        with st.form("edit_resource_form"):
            edit_name = st.text_input("New Name", key="edit_name")
            edit_type = st.selectbox(
                "New Type",
                ["", "PDF", "Video", "Textbook", "URL", "Image", "Other"],
                key="edit_type"
            )
            edit_desc = st.text_area("New Description", key="edit_desc")
            
            edit_submitted = st.form_submit_button(":material/save: Update Resource")
            
            if edit_submitted:
                update_data = {}
                if edit_name:
                    update_data["name"] = edit_name
                if edit_type:
                    update_data["type"] = edit_type
                if edit_desc:
                    update_data["description"] = edit_desc
                
                if update_data:
                    try:
                        response = requests.put(
                            f"{API_URL}/cr/resources/{resource_id_manage}",
                            json=update_data
                        )
                        if response.status_code == 200:
                            st.success(":material/check_circle: Resource updated successfully!")
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("No fields to update")
    
    # -------- Delete Resource --------
    with col2:
        st.markdown("#### :material/delete: Remove Resource")
        st.warning(":material/warning: Permanently deletes this resource")
        
        confirm_delete_resource = st.checkbox(
            "I confirm deletion",
            key="confirm_delete_resource"
        )
        
        if st.button(
            ":material/delete: Delete Resource",
            key="delete_resource_btn",
            type="secondary",
            use_container_width=True,
            disabled=not confirm_delete_resource
        ):
            try:
                response = requests.delete(
                    f"{API_URL}/cr/resources/{resource_id_manage}"
                )
                if response.status_code == 200:
                    st.success(":material/check_circle: Resource deleted successfully!")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

st.markdown("---")

# COURSE TOPICS SECTION
st.header(":material/topic: Course Topics")
st.markdown("View available topics for courses you tutor")

topic_col1, topic_col2 = st.columns([3, 1])

with topic_col1:
    topic_crn = st.text_input(
        "Filter by Course CRN",
        placeholder="12345",
        key="topic_crn_filter"
    )

with topic_col2:
    st.write("")  # Spacing
    view_topics_btn = st.button(
        ":material/list: View Topics",
        key="view_topics",
        use_container_width=True
    )

if view_topics_btn:
    try:
        url = f"{API_URL}/cr/topic"
        if topic_crn:
            url += f"?crn={topic_crn}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            topics = response.json()
            
            if topics:
                # Group topics by CRN
                topics_by_course = {}
                for topic in topics:
                    crn = topic['crn']
                    if crn not in topics_by_course:
                        topics_by_course[crn] = []
                    topics_by_course[crn].append(topic)
                
                # Display topics grouped by course
                for crn, course_topics in topics_by_course.items():
                    with st.expander(f":material/school: Course {crn} - {len(course_topics)} topics"):
                        for topic in course_topics:
                            st.badge(
                                f"{topic['name']} (ID: {topic['topicID']})",
                                color="blue"
                            )
                
                st.success(f":material/check_circle: Found {len(topics)} topic(s)")
            else:
                st.info("No topics found")
        else:
            st.error(f"Error fetching topics: {response.text}")
    
    except Exception as e:
        st.error(f"Connection error: {str(e)}")