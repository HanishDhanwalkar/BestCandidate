import streamlit as st
import os
import json

from helper import load_users, save_users, sanitize_filename
from constants import USERS_FILE, SCRAPED_DATA_DIR

def login_page():
    """Renders the login page for existing users."""
    st.title("Login to AI Candidate Scorer")

    st.markdown("Please enter your credentials to log in or create a new account.")

    with st.form("login_form"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            signup_button = st.form_submit_button("Sign Up (New User)")

        if login_button:
            users = load_users()
            if username in users and users[username]['password'] == password:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = username
                # Check if user has linkedin_url and if the scraped data file exists
                user_data = users[username]
                if user_data.get('linkedin_url') and os.path.exists(os.path.join(SCRAPED_DATA_DIR, sanitize_filename(user_data['linkedin_url']))):
                    st.session_state['page'] = 'apply_for_roles'
                else:
                    st.session_state['page'] = 'setup_profile'
                st.rerun() # Rerun to switch page
            else:
                st.error("Invalid username/email or password.")

        if signup_button:
            st.session_state['page'] = 'signup'
            st.rerun() # Rerun to switch page

def signup_page():
    """Renders the sign-up page for new users."""
    st.title("Sign Up for AI Candidate Scorer")

    st.markdown("Create your account to get started.")

    with st.form("signup_form"):
        new_username = st.text_input("Choose a Username or Email")
        new_password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submit_button = st.form_submit_button("Create Account")

        if signup_submit_button:
            users = load_users()
            if not new_username or not new_password or not confirm_password:
                st.error("All fields are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif new_username in users:
                st.error("Username or email already exists. Please choose another or log in.")
            else:
                # Store new user with password and without LinkedIn URL initially
                users[new_username] = {'password': new_password, 'linkedin_url': None, 'name': None}
                save_users(users)
                st.success("Account created successfully! Please proceed to set up your profile.")
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = new_username
                st.session_state['page'] = 'setup_profile'
                st.rerun() # Rerun to switch page

    if st.button("Back to Login"):
        st.session_state['page'] = 'login'
        st.rerun() # Rerun to switch page