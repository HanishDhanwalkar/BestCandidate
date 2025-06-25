import streamlit as st
import os
import json

from constants import USERS_FILE, SCRAPED_DATA_DIR
from helper import load_users, save_users, sanitize_filename

from LinkedIn_Scrapper.main import scrape_profile

def scrape_linkedin_profile(linkedin_url, user_name):
    filename = os.path.join(SCRAPED_DATA_DIR, sanitize_filename(linkedin_url))

    if os.path.exists(filename):
        st.info(f"LinkedIn data for {user_name} (from {linkedin_url}) already exists.")
        with open(filename, 'r') as f:
            return json.load(f)

    # st.warning(f"Simulating LinkedIn data scraping for {linkedin_url}...")
    scrapping = scrape_profile(linkedin_url)
    st.warning(f"{scrapping} for {linkedin_url}...")
    
def setup_profile_page():
    """Renders the profile setup page for new or incomplete profiles."""
    st.title("Set Up Your Profile")

    # Fetch current user data from the loaded users file
    current_user_data = load_users().get(st.session_state['current_user'])
    if not current_user_data:
        st.error("User data not found. Please log in again.")
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['page'] = 'login'
        st.rerun()
        return

    st.markdown("Please provide your name and LinkedIn profile URL to set up your profile.")

    with st.form("profile_setup_form"):
        # Pre-fill inputs if data already exists
        name = st.text_input("Your Name", value=current_user_data.get('name', ''))
        linkedin_url = st.text_input("Your LinkedIn Profile URL", value=current_user_data.get('linkedin_url', ''))
        submit_profile_button = st.form_submit_button("Save Profile and Continue")

        if submit_profile_button:
            if not name or not linkedin_url:
                st.error("Both Name and LinkedIn URL are required.")
            elif not (linkedin_url.startswith("http://") or linkedin_url.startswith("https://")) or "linkedin.com/in/" not in linkedin_url:
                st.error("Please enter a valid LinkedIn URL (e.g., https://www.linkedin.com/in/your-profile).")
            else:
                # Update user data with name and linkedin_url
                users = load_users()
                users[st.session_state['current_user']]['name'] = name
                users[st.session_state['current_user']]['linkedin_url'] = linkedin_url
                save_users(users)

                # Check if LinkedIn data for this URL has already been scraped
                filename = os.path.join(SCRAPED_DATA_DIR, sanitize_filename(linkedin_url))
                if not os.path.exists(filename):
                    st.info("LinkedIn profile data not found. Attempting to scrape...")
                    # Call the placeholder scraper. Replace with your actual API.
                    scraped_data = scrape_linkedin_profile(linkedin_url, name)
                    if scraped_data:
                        st.success("LinkedIn profile data simulated and saved!")
                        st.session_state['page'] = 'apply_for_roles'
                        st.rerun() # Rerun to switch page
                    else:
                        st.error("Failed to simulate LinkedIn data scraping. Please try again.")
                else:
                    st.success("Profile saved! LinkedIn data already exists. Redirecting to job applications...")
                    st.session_state['page'] = 'apply_for_roles'
                    st.rerun() # Rerun to switch page