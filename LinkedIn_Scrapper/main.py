import os
import json

from actions import login
from scraper import Person

from selenium import webdriver

from dotenv import load_dotenv


def main(linkedin_url):        
    load_dotenv(".env")

    PROXY_EMAIL_ID= os.getenv("PROXY_EMAIL_ID")
    PROXY_PASSWORD= os.getenv("PROXY_EMAIL_PASSWORD")

    driver = webdriver.Firefox()
    
    login(driver, PROXY_EMAIL_ID, PROXY_PASSWORD) 

    person = Person(linkedin_url=linkedin_url,  driver=driver, get=True, scrape=True)

    if driver:
        driver.quit()

    scapping_fields = [
        "linkedin_url",
        "name",
        "about",
        "location",
        "experiences",
        "educations",
        "interests",
        "accomplishments",
        # "also_viewed_urls",
        "contacts", 
    ]
    data = {key: getattr(person, key) for key in scapping_fields}

    def experience_to_dict(experience):
        return {
            'institution_name': experience.institution_name,
            'linkedin_url': experience.linkedin_url,
            'website': experience.website,
            'industry': experience.industry,
            'type': experience.type,
            'headquarters': experience.headquarters,
            'company_size': experience.company_size,
            'founded': experience.founded,
            'from_date': experience.from_date,
            'to_date': experience.to_date,
            'description': experience.description,
            'position_title': experience.position_title,
            'duration': experience.duration,
            'location': experience.location
        }
    def education_to_dict(education):
        return {
            'institution_name': education.institution_name,
            'linkedin_url': education.linkedin_url,
            'website': education.website,
            'industry': education.industry,
            'type': education.type,
            'headquarters': education.headquarters,
            'company_size': education.company_size,
            'founded': education.founded,
            'from_date': education.from_date,
            'to_date': education.to_date,
            'description': education.description,
            'degree': education.degree
        }
        
    # Define a function to convert the data to a JSON-serializable format
    def data_to_json(data):
        json_data = {}
        for key, value in data.items():
            if key == 'experiences':
                json_data[key] = [experience_to_dict(experience) for experience in value]
            elif key == 'educations':            
                json_data[key] = [education_to_dict(education) for education in value]
            else:
                json_data[key] = value
        return json_data

    # Save the data in a JSON file
    username = person.linkedin_url.split('/')[-2]
    filename = f"{username}.json"

    scarped_data_dir = './scraped_data'

    if not os.path.exists(scarped_data_dir):
        os.mkdir(scarped_data_dir)

    with open(os.path.join(scarped_data_dir, filename), 'w') as f:
        json.dump(data_to_json(data), f, indent=4)
        
if __name__ == "__main__":
    
    pass
    linkedin_url = ""
    main(linkedin_url)

