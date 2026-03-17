import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome back TA Admin, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Student & TA Management', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/14_Student_Directory.py')

if st.button('Study Session Requests', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/15_Session_Requests.py')

if st.button('Location Management', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Location_Management.py')


  