# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/40_About.py", label="About", icon="🧠")


#### ------------------------ Examples for Role of pol_strat_advisor ------------------------
def ProfessorHomeNav():
    st.sidebar.page_link(
        "pages/00_Professor_Home.py", label="Professor Home", icon="👤"
    )


def WorldBankVizNav():
    st.sidebar.page_link(
        "pages/01_World_Bank_Viz.py", label="World Bank Visualization", icon="🏦"
    )


def MapDemoNav():
    st.sidebar.page_link("pages/02_Map_Demo.py", label="Map Demonstration", icon="🗺️")


## ------------------------ Examples for Role of usaid_worker ------------------------

def TAAdminHomeNav():
    st.sidebar.page_link(
      "pages/10_TA_Admin_Home.py", label="TA Admin Home Page", icon=":material/home:"
    )

def StudentDirectoryNav():
    st.sidebar.page_link("pages/14_Student_Directory.py", label="Admin Directory", icon=":material/recent_actors:")

def SessionRequests():
    st.sidebar.page_link("pages/15_Session_Requests.py", label="Session Requests", icon=":material/person_raised_hand:")


def LocationManagement():
    st.sidebar.page_link(
        "pages/11_Location_Management.py", label="Location Directory", icon=":material/apartment:"
    )

def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )





#### ------------------------ Tutor Role ------------------------
def TutorHomeNav():
    st.sidebar.page_link("pages/30_Peer_Tutor_Home.py", label="Peer Tutor Home Page", icon="🏠")
    st.sidebar.page_link("pages/31_Course_Resources.py", label="Course Resources")
    st.sidebar.page_link("pages/32_Tutoring_Opportunities.py", label="Tutoring Opportunities")
    st.sidebar.page_link("pages/33_Student_Contacts.py", label="Student Contacts")


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.
        if st.session_state["role"] == "pol_strat_advisor":
           # PolStratAdvHomeNav()
            WorldBankVizNav()
            MapDemoNav()

        # If the user role is a ta admin, show the Api Testing page
        if st.session_state["role"] == "ta_admin":
            TAAdminHomeNav()
            StudentDirectoryNav()
            SessionRequests()
            LocationManagement()
            
            

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "tutor":
            TutorHomeNav()

    # # Always show the About page at the bottom of the list of links
    # AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
