import streamlit as st
import os
import json
import pandas as pd

from constants import USERS_FILE, SCRAPED_DATA_DIR, JDS_DIR
from helper import load_users, sanitize_filename, save_users


if not os.path.exists("./user_inputs.csv"):
    df = pd.DataFrame(columns=["user_linkedin_url", "JD", "score"])
    df.to_csv("./user_inputs.csv", index=False)

user_inputs = pd.read_csv("./user_inputs.csv")


def apply_for_roles_page():
    """Renders the page where users can view JDs and apply/get scores."""
    st.title("Apply for Roles")

    current_user_data = load_users().get(st.session_state['current_user'])
    # Ensure user is logged in and has a LinkedIn URL in their profile
    if not current_user_data or not current_user_data.get('linkedin_url'):
        st.warning("Please complete your profile setup first.")
        st.session_state['page'] = 'setup_profile'
        st.rerun()
        return

    st.markdown(f"Welcome, **{current_user_data.get('name', st.session_state['current_user'])}**! Select a job description to see your compatibility score.")

    # Load all Job Descriptions from the JDS_DIR
    jds = []
    for filename in os.listdir(JDS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(JDS_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    jd_data = json.load(f)
                    jds.append({"filename": filename, "data": jd_data})
            except json.JSONDecodeError:
                st.warning(f"Skipping malformed JD file: {filename}")

    if not jds:
        st.info(f"No Job Descriptions found in the '{JDS_DIR}' folder. Please add some JD.json files (e.g., 'Senior_Software_Engineer_JD.json').")
        # Provide a logout option even if no JDs are present
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['current_user'] = None
            st.session_state['page'] = 'login'
            st.rerun()
        return

    st.subheader("Available Job Descriptions:")

    # Load the candidate's own LinkedIn data (which should exist by now)
    user_linkedin_url = current_user_data['linkedin_url']
 
    # Display each JD with an expander and an "I'm interested" button
    for jd in jds:
        jd_filename = jd['filename']
        jd_title = jd['data'].get('job_title', 'N/A')
        jd_company = jd['data'].get('company', 'N/A')
        
        # Use st.expander for a collapsible view of the JD details
        with st.expander(f"**{jd_title}** at **{jd_company}**"):
            st.json(jd['data']) # Display full JD JSON content


            if st.button(f"I'm interested in {jd_title}", key=f"interest_button_{jd['filename']}"):                
                global user_inputs
                user_inputs.loc[-1] = [user_linkedin_url, jd_title, jd_filename, None]
                user_inputs.index = user_inputs.index + 1
                user_inputs = user_inputs.sort_index()
                
                print(user_inputs.head())
                
                user_inputs.to_csv("./user_inputs.csv", index=False)
                
                st.success(f"## You have successfully applied for {jd_title}.")
                
                
    # Logout button at the bottom of the page
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['page'] = 'login'
        st.rerun() # Rerun to go back to login page