import streamlit as st
import requests
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks
import pandas as pd
st.set_page_config(
    page_title="Session Requests Dashboard",
    page_icon="material/dashboard_2_edit:",
    layout="wide"
)


# Initialize sidebar
SideBarLinks()
st.title("Session Requests Dashboard")
st.markdown("Manage student study session requests and tags")
st.markdown("---")

API_URL = "http://api:4000"
tab1, tab2, tab3 = st.tabs(["Session Requests", "Tag Management", "TA Assignments"], width="stretch", default="Session Requests")

with tab1: 
    # DAHBOARD
    col1, col2, col3, col4 = st.columns(4)
    try:
        #pwnding
        pending_response = requests.get(f"{API_URL}/rt/session_requests?status=Pending")
        pending_count = len(pending_response.json()) if pending_response.status_code == 200 else 0
        #ones approved this week
        approved_response = requests.get(f"{API_URL}/rt/session_requests?status=Approved")
        approved_count = len(approved_response.json()) if approved_response.status_code == 200 else 0
        #tags
        tags_response = requests.get(f"{API_URL}/rt/tags")
        tag_count = len(tags_response.json()) if tags_response.status_code == 200 else 0
        # TA assignments
        assignments_response = requests.get(f"{API_URL}/pa/ta_assignments")
        assignment_count = len(assignments_response.json()) if assignments_response.status_code == 200 else 0
        
        with col1:
            st.metric(
                label=":material/hourglass: Pending Requests",
                value=pending_count,
                delta=None
            )
        with col2:
            st.metric(
                label=":material/bookmark_check: Approved",
                value=approved_count,
                delta=None
            )
        with col3:
            st.metric(
                label=":material/label: Total Tags",
                value=tag_count,
                delta=None
            )
        
        with col4:
            st.metric(
                label=":material/approval_delegation: Active Assignments",
                value=assignment_count,
                delta=None
            )

    except Exception as e:
        st.error(f"Error loading metrics: {str(e)}")

    st.markdown("---")

    # REQUESTS SECTION
    st.header(" Session Requests")

    # filter
    col1, col2 = st.columns([3, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Approved", "Completed"],
            key="status_filter"
        )
    with col2:
        st.write("") 
        refresh_requests = st.button(":material/refresh: Refresh", key="refresh_requests", use_container_width=True)

    #get requests
    if refresh_requests or status_filter:
        try:
            url = f"{API_URL}/rt/session_requests"
            if status_filter != "All":
                url += f"?status={status_filter}"
            
            response = requests.get(url)
            if response.status_code == 200:
                requests_data = response.json()
                
                if requests_data:
                    #loop through requests
                    for req in requests_data:
                        with st.container(border=True):
                            #request DI and status
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.markdown(f"### Request #{req['requestID']}")
                                st.caption(f" Created: {req['dateCreated']}")
                            
                            with col2:
                                
                                if req['status'] == 'Pending':
                                    st.badge("Pending", icon=":material/hourglass:", color="yellow", width="content")
                                elif req['status'] == 'Approved':
                                    st.badge("Approved", icon =":material/thumb_up:", color="green", width="content")
                                elif req['status'] == 'Completed':
                                    st.badge("Completed", color="gray", width="content")
                                
                            
                                if req.get('tags'):
                                    st.write("**Tags:**")
                                    tag_names = req['tags'].split(',')
                                    tag_cols = st.columns(len(tag_names))
                                    for i, tag in enumerate(tag_names):
                                        with tag_cols[i]:
                                            st.badge(label=tag, color="blue")
                            
                            with col3:
                                #action buttons
                                if req['status'] == 'Pending':
                                    if st.button("Approve", key=f"approve_{req['requestID']}", use_container_width=True, type="primary", 
                                                icon = ":material/check:"):
                                        try:
                                            approve_response = requests.put(
                                                f"{API_URL}/rt/session_requests/{req['requestID']}",
                                                json={"status": "Approved"}
                                            )
                                            if approve_response.status_code == 200:
                                                st.success("Request approved!")
                                                st.rerun()
                                            else:
                                                st.error("Approval failed")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                                    
                                    if st.button(" Reject", key=f"reject_{req['requestID']}", use_container_width=True, 
                                                icon = ":material/close:"):
                                        try:
                                            delete_response = requests.delete(
                                                f"{API_URL}/rt/session_requests/{req['requestID']}"
                                            )
                                            if delete_response.status_code == 200:
                                                st.success("Request rejected!")
                                                st.rerun()
                                            else:
                                                st.error("Rejection failed")
                                        except Exception as e:
                                            st.error(f"Error: {str(e)}")
                            
                            # Student names
                            if req.get('studentFirstNames'):
                                st.write(f"** Requesting Students:** {req['studentFirstNames']}")
                            
                            #more info/details button
                            if st.button(" View Details", key=f"details_{req['requestID']},", icon = ":material/search_gear:"):
                                try:
                                    detail_response = requests.get(f"{API_URL}/rt/session_requests/{req['requestID']}")
                                    if detail_response.status_code == 200:
                                        details = detail_response.json()
                                        st.json(details)
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    st.success(f"✅ Showing {len(requests_data)} request(s)")
                else:
                    st.info("No session requests found")
            else:
                st.error(f"Error fetching requests: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

    st.markdown("---")

with tab2: 
    # TAG MANAGEMENT SECTION ====================
    st.header(" Tag Management")
    st.markdown("Find and merge duplicate tags to keep requests organized")

    tag_tab1, tag_tab2, tag_tab3 = st.tabs(["View Tags", "Create Tag", "Merge/Delete Tags"])

    #tab 1: view tags
    with tag_tab1:
        st.subheader("Search Tags")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_tag = st.text_input(
                "Search for similar tags",
                placeholder="git (finds 'git help', 'GitHub help', etc.)",
                key="search_tags"
            )
        with col2:
            # st.write(" ")
            search_btn = st.button(":material/category_search: Search", key="search_tags_btn", use_container_width=True)
        
        if search_btn:
            try:
                url = f"{API_URL}/rt/tags"
                if search_tag:
                    url += f"?search={search_tag}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    tags = response.json()
                    if tags:
                        st.write(f"**Found {len(tags)} matching tag(s):**")
                        
                        for tag in tags:
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col1:
                                st.write(f"**ID: {tag['tagID']}**")
                            with col2:
                                badge_type = "primary" if tag['studentCreated?'] == 0 else "secondary"
                                st.badge(tag['tagName'])
                            with col3:
                                creator = "👤 Student" if tag['studentCreated?'] == 1 else "👨‍🏫 Admin"
                                st.write(creator)
                    else:
                        st.info("No tags found")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")


    # tab 2: create new tag
    with tag_tab2:
        st.subheader("Create New Standardized Tag")
        
        with st.form("create_tag_form"):
            new_tag_name = st.text_input("Tag Name *", placeholder="SQL Help")
            student_created = st.checkbox("Student Created", value=False)
            
            st.markdown("*Required fields")
            submitted = st.form_submit_button("➕ Create Tag", type="primary")
            
            if submitted:
                if not new_tag_name:
                    st.error("Please enter a tag name")
                else:
                    tag_data = {
                        "tagName": new_tag_name,
                        "studentCreated": 1 if student_created else 0
                    }
                    try:
                        response = requests.post(f"{API_URL}/rt/tags", json=tag_data)
                        if response.status_code == 201:
                            st.success(f"Tag '{new_tag_name}' created!")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
    # tab 3: merge / delete tags
    with tag_tab3:
        st.subheader("Manage Duplicate Tags")
        
        st.info("Use the search feature in 'View Tags' to find duplicate tags like 'git help' and 'GitHub help'")
        
        col1, col2 = st.columns(2)
        
        # Merge tags
        with col1:
            st.markdown("#### Merge Duplicate Tags")
            
            with st.form("merge_tags_form"):
                st.write("Consolidate two similar tags into one")
                source_tag_id = st.number_input(
                    "Tag ID to Remove",
                    min_value=1,
                    step=1,
                    key="source_tag",
                    help="This tag will be deleted after merging"
                )
                target_tag_id = st.number_input(
                    "Tag ID to Keep",
                    min_value=1,
                    step=1,
                    key="target_tag",
                    help="All references will point to this tag"
                )
                merge_submitted = st.form_submit_button(":material/merge_type: Merge Tags", type="primary")
                if merge_submitted:
                    if source_tag_id == target_tag_id:
                        st.error(":material/close: Cannot merge a tag into itself!")
                    else:
                        merge_data = {"mergeIntoTagID": target_tag_id}
                        try:
                            response = requests.put(f"{API_URL}/rt/tags/{source_tag_id}", json=merge_data)
                            if response.status_code == 200:
                                st.success(f":material/check: Tag {source_tag_id} merged into {target_tag_id}!")
                                st.balloons()
                            else:
                                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
        
        # deleteing tag
        with col2:
            st.markdown("#### :material/delete: Delete Tag")
            st.warning("⚠️ Permanently removes tag and all associations")
            
            delete_tag_id = st.number_input(
                "Tag ID to Delete",
                min_value=1,
                step=1,
                key="delete_tag"
            )
            confirm_tag_delete = st.checkbox("I'm sure", key="confirm_tag_delete")
            if st.button(
                ":material/delete: Delete Tag",
                disabled=not confirm_tag_delete,
                key="delete_tag_btn",
                use_container_width=True,
                type="secondary"
            ):
                try:
                    response = requests.delete(f"{API_URL}/rt/tags/{delete_tag_id}")
                    if response.status_code == 200:
                        st.success("Tag deleted successfully!")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    st.markdown("---")

with tab3: 
    # ASSIGNING TA'S SESSION==========================================

    st.header(" Assign TAs to Study Sessions")
    col1, col2 = st.columns(2)
    with col1:
        with st.form("assign_ta_form"):
            st.markdown("**Assign TA to Session**")
            assign_ta_id = st.number_input("TA NU ID *", min_value=1000000, max_value=9999999, value=1567890, step=1)
            assign_session_id = st.number_input("Session ID *", min_value=1, step=1, value=1001)
            assign_submitted = st.form_submit_button("➕ Assign TA", type="primary", use_container_width=True)
            
            if assign_submitted:
                assignment_data = {
                    "taID": assign_ta_id,
                    "sessionID": assign_session_id
                }
                try:
                    response = requests.post(f"{API_URL}/pa/ta_assignments", json=assignment_data)
                    if response.status_code == 201:
                        st.success("TA assigned to session!")
                        st.balloons()
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    with col2:
        st.markdown("**Current TA Assignments**")
        if st.button(":material/approval_delegation: View Assignments", key="view_assignments", use_container_width=True):
            try:
                #alayna check this url later
                response = requests.get(f"{API_URL}/pa/ta_assignments")
                if response.status_code == 200:
                    assignments = response.json()
                    if assignments:
                        df = pd.DataFrame(assignments)
                        st.dataframe(
                            df[['taID', 'sessionID', 'firstName', 'lastName']],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info("No TA assignments found")
                else:
                    st.error("Error fetching assignments")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")