import json
import os

import streamlit as st
import re

from constants import USERS_FILE

def  load_users():
    """
    Loads user data from the users.json file.
    Handles cases where the file might be missing, empty, or contain invalid JSON.
    """
    if not os.path.exists(USERS_FILE):
        # If file doesn't exist, create it with an empty JSON object
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(USERS_FILE, 'r') as f:
            # Check if the file is empty before attempting to load
            file_content = f.read()
            if not file_content:
                st.warning(f"{USERS_FILE} is empty. Initializing with empty user data.")
                # If empty, write an empty JSON object to it
                with open(USERS_FILE, 'w') as wf:
                    json.dump({}, wf)
                return {}
            # If not empty, try to load JSON
            return json.loads(file_content)
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from {USERS_FILE}. The file might be corrupted. Re-initializing.")
        # If decoding fails, re-create the file with an empty JSON object
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred while loading {USERS_FILE}: {e}. Re-initializing.")
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    
def save_users(users):
    """Saves user data to the users.json file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)
        
def sanitize_filename(url):
    """
    Converts a LinkedIn URL into a safe filename by extracting the username
    and sanitizing it.
    Example: https://www.linkedin.com/in/john-doe-123456789/ -> john-doe-123456789.json
    """
    match = re.search(r'linkedin\.com/in/([^/\\?]+)', url)
    if match:
        username = match.group(1)
        # Remove any characters that are not alphanumeric, underscore, or hyphen
        safe_username = re.sub(r'[^\w-]', '', username)
        return f"{safe_username}.json"
    # Fallback for invalid URLs, although validation should prevent this
    return "default_profile.json"