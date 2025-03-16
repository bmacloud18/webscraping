import os
import pandas as pd
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

# Add custom stopwords


# Load API key from .env file
load_dotenv()

FIRST_NAME = os.getenv("FIRST_NAME")
LAST_NAME = os.getenv("LAST_NAME")
CITY = os.getenv("CITY")
ADDRESS = os.getenv("ADDRESS")
STATE = os.getenv("STATE")
ZIP = os.getenv("ZIP")
COUNTRY = os.getenv("COUNTRY")
PHONE_NUM = os.getenv("PHONE_NUM")
EMAIL = os.getenv("EMAIL")


link = "https://www.pokemoncenter.com/product/100-10356/pokemon-tcg-scarlet-and-violet-journey-together-pokemon-center-elite-trainer-box"

add_class = "add-to-cart-button--PZmQF"

shipping_details = [
    ["first_id", "shipping-givenName"],
    ["last_id", "shipping-familyName"],
    ["address_id", "shipping-streetAddress"],
    ["city_id", "shipping-locality"],
    ["state_id", "shipping-region"],
    ["zip_id", "shipping-postalCode"],
    ["country_id", "shipping-countryName"],
    ["phone_id", "shipping-phoneNumber"],
    ["email_id", "shipping-email"]
    ]
    
billing_id =  "billing-selector"


continue_class = "btn--ICBoB"


# Set up Selenium WebDriver (make sure to have ChromeDriver installed)
driver = webdriver.Chrome()


driver.get(link)


dropdown = Select(driver.find_element(By.ID, f"{state_id}"))
dropdown.select_by_visible_text(f"{STATE}")  # Replace with actual option text


dropdown = Select(driver.find_element(By.ID, f"{billing_id}"))
dropdown.select_by_visible_text("Credit/Debit Card")  # Replace with actual option text

try:
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, f"{add_class}"))
    )
    button.click()
except:
    print("error occurred finding add button")

try:
    WebDriverWait(driver, 20).until(
        dropdown = Select(EC.presence_of_all_elements_located((By.ID, f"{billing_id}")))
    )
except:
    print("billing not available")

driver.quit()