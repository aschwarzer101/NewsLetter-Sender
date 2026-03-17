import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome back Peer Tutor, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View + Manage Course Resources', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/31_Course_Resources.py')

if st.button('Find Tutoring Opportunities', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/32_Tutoring_Opportunities.py')

if st.button('Contact Students', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/33_Student_Contacts.py')
  