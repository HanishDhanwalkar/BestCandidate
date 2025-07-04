import json
import os
import pandas as pd
import numpy as np

import google.generativeai as genai
from dotenv import load_dotenv


from constants import USERS_FILE, SCRAPED_DATA_DIR, JDS_DIR
from helper import load_users, sanitize_filename


# --- Gemini Backend Logic for Scoring ---
# Configuration and Initialization
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Gemini API Key not found. Please set GEMINI_API_KEY in your .env file.")
    
def get_gemini_response(prompt_parts):
    """Sends a prompt to the Gemini API and returns the text response."""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash") # Using gemini-pro for text generation
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
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

score:
"""
    response_text = get_gemini_response([prompt])
    if response_text:
        try:
            # Attempt to extract the integer score from the response
            # This handles cases where Gemini might return "score: 85" or similar
            score = int("".join(filter(str.isdigit, response_text)))
            return max(0, min(100, score)) # Ensure score is within 0-100 range
        except ValueError:
            print(f"Could not parse score from Gemini response: '{response_text}'. Please refine the prompt.")
            return None
    return None


if __name__ == "__main__":
    user_inputs_df = pd.read_csv("./user_inputs.csv")
    
    for idx, user_input in user_inputs_df.iterrows():
        print(idx)
        if str(user_input['score']) == "nan":
            print("scoring for ", user_input['user_linkedin_url'], "and", user_input['JD'])
        else:
            print("already scored for ", user_input['user_linkedin_url'], "and", user_input['JD'], "with score", user_input['score'])
            continue
            
            
        # Load the candidate's own LinkedIn data (which should exist by now)
        user_linkedin_url = user_input['user_linkedin_url']
        candidate_filename = os.path.join(SCRAPED_DATA_DIR, sanitize_filename(user_linkedin_url))

        # Double-check if the candidate's scraped data file exists
        if not os.path.exists(candidate_filename):
            print(f"Your LinkedIn data ({candidate_filename}) was not found. Please re-do profile setup to generate it.")
            continue

        # Load the candidate's own LinkedIn data
        try:
            with open(candidate_filename, 'r') as f:
                candidate_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error loading your LinkedIn data from {candidate_filename}. The file might be corrupted. Please re-do profile setup.")
            continue
        
        filename = user_input['jd_filename']
        jd_filepath = os.path.join(JDS_DIR, filename)
        try:
            with open(jd_filepath, 'r') as f:
                jd_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Skipping malformed JD file: {filename}")
    
        score = score_candidate(jd_data, candidate_data) # Call the scoring function
        user_inputs_df.loc[idx, 'score'] = score
        

            
    user_inputs_df.to_csv("./user_inputs.csv", index=False)