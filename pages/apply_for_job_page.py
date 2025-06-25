import streamlit as st
import os
import json

from constants import USERS_FILE, SCRAPED_DATA_DIR, JDS_DIR
from helper import load_users, sanitize_filename, save_users

import google.generativeai as genai


# --- Gemini Backend Logic for Scoring ---
def get_gemini_response(prompt_parts):
    """Sends a prompt to the Gemini API and returns the text response."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash") # Using gemini-pro for text generation
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Gemini API: {e}")
        return None

def score_candidate(job_description_json, candidate_data_json):
    """
    Scores a candidate based on a job description and their LinkedIn profile data
    using the Gemini API.
    """
    prompt = f"""
    You are an AI-powered recruitment assistant. Your task is to score a candidate based on a given job description and their LinkedIn profile data.
    The score should be between 0 and 100, where 100 is a perfect match.

    Consider the following aspects for scoring:
    - **Mandatory Skills:** High penalty if not present.
    - **Weighted Skills:** Factor in the 'weight' of each skill from the JD.
    - **Required Experience Years:** Assess the candidate's professional experience against this.
    - **Required Education:** Match the candidate's education level.
    - **Keywords:** Look for these keywords in 'about', 'description' fields within experience and education, and skill sections.
    - **Overall Fit:** Evaluate the 'about' section and overall career trajectory for alignment with the role.

    Return ONLY the score as an integer (e.g., 85). Do not include any other text or explanation.

    Here is the Job Description:
    {json.dumps(job_description_json, indent=2)}

    Here is the Candidate's LinkedIn Profile Data:
    {json.dumps(candidate_data_json, indent=2)}

    Score:
    """
    response_text = get_gemini_response([prompt])
    if response_text:
        try:
            # Attempt to extract the integer score from the response
            # This handles cases where Gemini might return "Score: 85" or similar
            score = int("".join(filter(str.isdigit, response_text)))
            return max(0, min(100, score)) # Ensure score is within 0-100 range
        except ValueError:
            st.error(f"Could not parse score from Gemini response: '{response_text}'. Please refine the prompt.")
            return None
    return None

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
    candidate_filename = os.path.join(SCRAPED_DATA_DIR, sanitize_filename(user_linkedin_url))

    # Double-check if the candidate's scraped data file exists
    if not os.path.exists(candidate_filename):
        st.error(f"Your LinkedIn data ({candidate_filename}) was not found. Please re-do profile setup to generate it.")
        if st.button("Go to Profile Setup"):
            st.session_state['page'] = 'setup_profile'
            st.rerun()
        return

    try:
        with open(candidate_filename, 'r') as f:
            candidate_data = json.load(f)
    except json.JSONDecodeError:
        st.error(f"Error loading your LinkedIn data from {candidate_filename}. The file might be corrupted. Please re-do profile setup.")
        return

    # Display each JD with an expander and an "I'm interested" button
    for jd in jds:
        jd_title = jd['data'].get('job_title', 'N/A')
        jd_company = jd['data'].get('company', 'N/A')
        
        # Use st.expander for a collapsible view of the JD details
        with st.expander(f"**{jd_title}** at **{jd_company}**"):
            st.json(jd['data']) # Display full JD JSON content

            # Button to trigger scoring for this specific JD
            # Use a unique key for each button
            if st.button(f"I'm interested in {jd_title}", key=f"interest_button_{jd['filename']}"):
                st.info(f"Calculating score for {jd_title}...")
                score = score_candidate(jd['data'], candidate_data) # Call the scoring function
                if score is not None:
                    st.success(f"## Your Score for {jd_title}: {score}/100")
                    if score >= 80:
                        st.balloons() # Fun animation for high scores
                    elif score < 50:
                        st.warning("You might not be a strong fit for this role based on the current scoring.")
                else:
                    st.error("Failed to generate score for this role. Please try again.")

    # Logout button at the bottom of the page
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['current_user'] = None
        st.session_state['page'] = 'login'
        st.rerun() # Rerun to go back to login page