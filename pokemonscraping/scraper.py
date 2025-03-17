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
CARD_NUM = os.getenv("CARD_NUM")
CVV2 = os.getenv("CVV2")
MONTH = os.getenv("MONTH")
YEAR = os.getenv("YEAR")


link = "https://www.pokemoncenter.com/product/100-10356/pokemon-tcg-scarlet-and-violet-journey-together-pokemon-center-elite-trainer-box"

add_class = "add-to-cart-button--PZmQF"

shipping_details = [
    [FIRST_NAME, "shipping-givenName"],
    [LAST_NAME, "shipping-familyName"],
    [ADDRESS, "shipping-streetAddress"],
    [CITY, "shipping-locality"],
    [ZIP, "shipping-postalCode"],
    [COUNTRY, "shipping-countryName"],
    [PHONE_NUM, "shipping-phoneNumber"],
    [EMAIL, "shipping-email"]
]

shipping_dropdowns = [
    [STATE, "shipping-region"]
]
payment_dropdown = [
    ["Credit/Debit Card", "billing-selector"]
]
card_details = [
    [CARD_NUM, "number"],
    [CVV2, "securityCode"]
]
card_dropdowns = [
    [MONTH, "expiryMonth"],
    [YEAR, "expiryYear"]
]



continue_class = "btn--ICBoB"


# Set up Selenium WebDriver (make sure to have ChromeDriver installed)
driver = webdriver.Chrome()


driver.get(link)

def iterate_dropdowns(dropdown_list):
    for element in dropdown_list:
        try:
            dropdown = Select(WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, f"{element[1]}")) # option id
            ))
            dropdown.select_by_visible_text(f"{element[0]}")  # option text
        except:
            print("error occurred iterating dropdowns")
try:
    button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, f"{add_class}"))
    )
    button.click()
except:
    print("error occurred finding add button")

try:
    WebDriverWait(driver, 20).until(
        dropdown = Select(EC.presence_of_element_located((By.ID, f"{billing_id}")))
    )
except:
    print("billing not available")

driver.quit()