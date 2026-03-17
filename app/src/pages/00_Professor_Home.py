import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Professor, {st.session_state['first_name']}!")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Manange Course Materials', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_Professor_Course_Materials.py')

if st.button('View Student Analytics Dashboard', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Professor_Student_Analytics.py')

if st.button('Create New Course', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/03_Create_New_Course.py')