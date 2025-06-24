import getpass
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

REMEMBER_PROMPT = 'remember-me-prompt__form-primary'
VERIFY_LOGIN_ID = "global-nav__primary-link"

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

def login(driver, email, password, cookie=None, timeout=10):
    print("Logging in...")
    if cookie is not None:
        return _login_with_cookie(driver, cookie)
  
    driver.get("https://www.linkedin.com/login")
    element = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.ID, "username")))
  
    email_elem = driver.find_element(By.ID,"username")
    email_elem.send_keys(email)
    password_elem = driver.find_element(By.ID,"password")
    password_elem.send_keys(password)
    password_elem.submit()
  
    if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
        remember = driver.find_element(By.ID,REMEMBER_PROMPT)
        if remember:
            remember.submit()
  
    element = WebDriverWait(driver, timeout).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, VERIFY_LOGIN_ID)))
  
def _login_with_cookie(driver, cookie):
    driver.get("https://www.linkedin.com/login")
    driver.add_cookie({
      "name": "li_at",
      "value": cookie
    })