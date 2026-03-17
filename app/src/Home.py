##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")
st.title('StudyPack')
st.write('\n\n')
# st.write('### Overview:')
# st.write('\n')
st.write('#### HI! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user 
# can click to MIMIC logging in as that mock user. 

if st.button("Act as Anna Smith, a Northeastern professor", 
            type = 'primary', 
            use_container_width=True):
    # when user clicks the button, they are now considered authenticated
    st.session_state['authenticated'] = True
    # we set the role of the current user
    st.session_state['role'] = 'Professor'
    # we add the first name of the user (so it can be displayed on 
    # subsequent pages). 
    st.session_state['first_name'] = 'Anna'
    # finally, we ask streamlit to switch to another page, in this case, the 
    # landing page for this particular user type
    logger.info("Logging in as Anna Smith, Professor Data Administrator Persona")
    st.switch_page('pages/00_Professor_Home.py')

if st.button('Act as Gabby Gutierrez, a TA administrator', 
            type = 'primary', 
            use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'ta_admin'
    st.session_state['first_name'] = 'Gabby'
    logger.info("logging in as TA administrator")
    st.switch_page('pages/10_TA_Admin_Home.py')

if st.button('Act as Jean-Baptiste Clamence, a Computer Science Student', 
            type = 'primary', 
            use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'student'
    st.session_state['first_name'] = 'Jean-Baptiste'
    st.switch_page('pages/20_Admin_Home.py')

if st.button('Act as John Adams, a Peer Tutor for CS Students', 
        type = 'primary',
        use_container_width=True): 
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'tutor'
    st.session_state['first_name'] = 'John Adams'
    st.switch_page('pages/30_Peer_Tutor_Home.py')

