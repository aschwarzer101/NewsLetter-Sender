

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(
    page_title="Location Management",
    page_icon=":material/apartment:",
    layout="wide"
)

SideBarLinks()
st.title("Location Management :material/apartment:")
st.markdown("Manage study locations for sessions")
st.markdown("---")

API_URL = "http://api:4000"




loc_tab1, loc_tab2, loc_tab3= st.tabs([":material/location_on: View Locations", ":material/add_location_alt: Add Study Location", "Edit Study Location"])

## view + update locations tab: 
with loc_tab1: 
    st.header(":material/location_on: Study Locations")
    col1, col2 = st.columns([2, 2])
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive"],
            key="status_filter"
        )
    with col2:
        st.write("") 
        refresh_locations = st.button(":material/refresh: Refresh", key="refresh_locations", use_container_width=True)
    #get locations
        # building_filter = st.selectbox(
        #     "Filter by Building",
        #     ["All Buildings"],
        #     key="building_filter"
        # )
    if refresh_locations or status_filter or 'first_load' not in st.session_state:
        st.session_state.first_load = True
        try:
            url = f"{API_URL}/si/study_location"
            
            response = requests.get(url)
            if response.status_code == 200:
                locations_data = response.json()
                
                # extract values for filters: 
                #buildings = sorted(list(set(location["building"] for location in locations_data )))
                
                if locations_data:
                    unique_buildings = sorted(list(set([loc['building'] for loc in locations_data])))
                    if len(unique_buildings) > 0:
                        building_filter = st.selectbox(
                            "Filter by Building",
                            ["All Buildings"] + unique_buildings,
                            key="building_filter_updated"
                        )
                
                # Apply filters
                filtered_locations = locations_data
                
                if building_filter != "All Buildings":
                    filtered_locations = [loc for loc in filtered_locations if loc['building'] == building_filter]
                
                if status_filter == "Active":
                    filtered_locations = [loc for loc in filtered_locations if loc.get('status') == 1]
                elif status_filter == "Inactive":
                    filtered_locations = [loc for loc in filtered_locations if loc.get('status') == 0]
                
                if filtered_locations:
                    for loc in filtered_locations:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                st.markdown(f"### {loc['building']} - Room {loc['room']}")
                                st.caption(f":material/location_on: Location ID: {loc['locID']}")
                            
                            with col2:
                                st.write(f"**Capacity:** {loc['capacity']} people")
                                
                                if loc.get('status') == 1:
                                    st.badge("Active", icon=":material/check_circle:", color="green", width="content")
                                else:
                                    st.badge("Inactive", icon=":material/cancel:", color="red", width="content")
                            
                            
                    
                    st.success(f"✅ Showing {len(filtered_locations)} location(s)")
                else:
                    st.info("No locations found matching your filters")
            else:
                st.error(f"Error fetching locations: {response.text}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
with loc_tab2: 
    st.subheader("Add New Location")
    
    with st.form("add_location_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_capacity = st.text_input("capacity", placeholder=" ")
            new_room = st.text_input("room", placeholder= "ex:Lab 201")
            new_building = st.text_input("building", placeholder= "ex:West Village H")
            
        
        with col2:
            new_status = st.selectbox("Status", ["Active","InActive"])
        submitted = st.form_submit_button("Add Location")
        
        if submitted:
            #submit form data
            location_data = {
                "status": int(0) if new_status=="InActive" else int(1), 
                "capacity": new_capacity,
                "room": new_room,
                "building": new_building
            }
            
            try:
                response = requests.post(f"{API_URL}/si/study_location", json=location_data) 
                if response.status_code == 201:
                    st.success(f"added successfully!")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")
    st.markdown("---")
with loc_tab3: 
    st.subheader("Edit Study Location Info")
    
    # location search
    loc_id = st.text_input("Enter locationID", placeholder="ex: 6", key="manage_locID")
    
    # Look up location button
    if loc_id and st.button(":material/category_search:  Look Up Location", key="lookup_location"):
        try:
            response = requests.get(f"{API_URL}/si/study_location/{loc_id}")
            if response.status_code == 200:
                location = response.json()
                st.success(f"Found: {location['room']} {location['building']}")
                
                # Display student info in a nice format
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Building:** {location['building']}")
                    st.write(f"**Room:** {location['room']}")
                    st.write(f"**Capacity:** {location['capacity']}")
                with col2:
                    st.write(f"**Status:** {location['status']}")
            else:
                st.error("Location not found")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # columns for deleting/editing
    col1, col2 = st.columns(2)
    
    # update location info
    with col1:
        st.header("Edit Location Info")
        with st.form("update_location_form"):
            update_capacity = st.text_input("New Capacity", key="update_capacity")
            update_status = st.selectbox("Update Status", 
                ["Active", "InActive", ], key="update_status")
            
            update_submitted = st.form_submit_button(" :material/edit_location_alt: Update Info")
            
            if update_submitted:
                if loc_id:
                    update_data = {}
                    if update_capacity:
                        update_data["capacity"] = update_capacity
                    if update_status:
                        update_data["status"] = update_capacity
                    if update_data:
                        try:
                            response = requests.put(f"{API_URL}/si/study_location/{loc_id}", json=update_data)
                            if response.status_code == 200:
                                st.success("Location updated successfully!")
                            else:
                                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")
                    else:
                        st.warning("No fields to update")
                else:
                    st.warning("Please enter a location ID")
    
    # Remove Location
    with col2:
        st.markdown("####  Remove Location")
        st.warning("⚠️ Permanently removes location")
        
        confirm_delete = st.checkbox("Delete this location", key="confirm_delete")
        
        if st.button(" :material/delete_forever: Remove Location", key="delete_location", type="secondary", use_container_width=True, disabled=not confirm_delete):
            if loc_id:
                try:
                    response = requests.delete(f"{API_URL}/si/study_location/{loc_id}")
                    if response.status_code == 200:
                        st.success("Location removed successfully!")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a location ID first")
