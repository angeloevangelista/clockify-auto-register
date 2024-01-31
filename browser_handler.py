import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from dotenv import load_dotenv

load_dotenv()

def get_authorization_token() -> tuple[str, str]:
  browser_driver: BaseWebDriver = None

  try:
    portal_url = 'https://apontamentos.lab2dev.com/'
    webmail_url = 'https://webmail.lab2dev.com/'

    user_email = os.environ['LAB2DEV_USER_EMAIL']
    user_password = os.environ['LAB2DEV_USER_PASSWORD']

    webdriver_service = Service(GeckoDriverManager().install())

    browser_options = webdriver.FirefoxOptions()
    browser_options.headless = True
    
    browser_driver = webdriver.Firefox(
      service=webdriver_service,
      options=browser_options,
    )

    browser_driver.get(portal_url)

    portal_email_input = browser_driver.find_element(
      By.CSS_SELECTOR,
      'input[type=email]',
    )
    portal_email_input.clear()
    portal_email_input.send_keys(user_email)
    portal_email_input.send_keys(Keys.RETURN)

    portal_otp_confirm_button = WebDriverWait(browser_driver, 30).until(
      expected_conditions.element_to_be_clickable((
        By.CSS_SELECTOR, 'button[type=submit]',
      ))
    )

    portal_tab_handle = browser_driver.current_window_handle
    browser_driver.switch_to.new_window('tab')

    browser_driver.get(webmail_url)

    webmail_email_input = browser_driver.find_element(By.ID, 'user')
    webmail_email_input.clear()
    webmail_email_input.send_keys(user_email)
    
    webmail_password_input = browser_driver.find_element(By.ID, 'pass')
    webmail_password_input.clear()
    webmail_password_input.send_keys(user_password)

    browser_driver.find_element(By.ID, 'login_submit').click()

    roundcube_mail_anchor = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.ID, 'lnkUserPrefroundcube',
      ))
    )
    
    browser_driver.get(roundcube_mail_anchor.get_attribute('href'))

    first_message_item = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.ID, 'messagelist',
      ))
    ).find_element(
      By.CSS_SELECTOR,
      'tbody > tr:nth-child(1)',
    )

    ActionChains(browser_driver).double_click(first_message_item).perform()

    message_body_div = WebDriverWait(browser_driver, 30).until(
      expected_conditions.presence_of_element_located((
        By.ID, 'messagebody',
      ))
    )
    
    one_time_password = message_body_div.find_elements(
      By.TAG_NAME, 'strong',
    )[2].text

    delete_email_button = browser_driver.find_element(
      By.CSS_SELECTOR,
      'a.button.delete',
    )

    delete_email_button.click()

    browser_driver.close()
    browser_driver.switch_to.window(portal_tab_handle)

    otp_inputs = browser_driver.find_elements(By.TAG_NAME, 'input')

    for index in range(len([*one_time_password])):
      otp_inputs[index].send_keys(one_time_password[index])

    portal_otp_confirm_button.click()

    WebDriverWait(browser_driver, 30).until(
      expected_conditions.url_to_be(portal_url)
    )

    access_token = browser_driver.get_cookie('portal-lab__auth-access-token').get('value')
    refresh_token = browser_driver.get_cookie('portal-lab__auth-refresh-token').get('value')

    browser_driver.close()

    return access_token, refresh_token
  finally:
    if browser_driver: browser_driver.quit()
