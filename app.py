import streamlit as st
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
import re 

from LinkedIn_Scrapper.main import scrape_profile

from constants import USERS_FILE, SCRAPED_DATA_DIR, JDS_DIR
from helper import load_users, save_users, sanitize_filename

from pages.login_page import login_page, signup_page
from pages.setup_profile_page import setup_profile_page
from pages.apply_for_job_page import apply_for_roles_page

# --- Configuration and Initialization ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("Gemini API Key not found. Please set GEMINI_API_KEY in your .env file.")
    st.stop()

# Ensure directories exist
os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)
os.makedirs(JDS_DIR, exist_ok=True)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'login' # Initial page is the login page

# --- Main Application Flow Control ---
def main():
    """Controls the page navigation based on session state."""
    st.set_page_config(page_title="AI Candidate Scorer", layout="wide") # Set app wide layout

    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
    elif st.session_state['page'] == 'setup_profile':
        # Ensure user is logged in before allowing profile setup
        if not st.session_state['logged_in']:
            st.session_state['page'] = 'login'
            st.rerun()
        else:
            setup_profile_page()
    elif st.session_state['page'] == 'apply_for_roles':
        # Ensure user is logged in before allowing access to job applications
        if not st.session_state['logged_in']:
            st.session_state['page'] = 'login'
            st.rerun()
        else:
            apply_for_roles_page()

# Entry point of the Streamlit application
if __name__ == "__main__":
    main()