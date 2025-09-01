import time
import pandas as pd
import re
import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load Excel file
file_path = "pan.xlsx"
if not os.path.exists(file_path):
    print(f"Error: File '{file_path}' not found!")
    exit()

df = pd.read_excel(file_path, engine='openpyxl')
df.columns = df.columns.str.strip()  # Remove unwanted spaces

if "PAN" not in df.columns:
    print(f"Error: 'PAN' column not found! Available columns: {df.columns.tolist()}")
    exit()

# Added support for multiple OS
current_os = platform.system()
driver_folder = os.path.dirname(os.path.abspath(__file__))
if current_os == "Windows":
    driver_path = os.path.join(driver_folder, "msedgedriver.exe")
elif current_os == "Linux":
    driver_path = os.path.join(driver_folder, "msedgedriver")
else:
    raise Exception(f"Unsupported OS: {current_os}")

# Set up Edge WebDriver in headless mode
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

# Ensure latest version of Edge is used (Windows will automatically use the latest version)
if current_os == "Linux":
    options.binary_location = "/usr/bin/microsoft-edge-stable"

# Initialize driver:
service = Service(driver_path)
driver = webdriver.Edge(service=service, options=options)

def solve_captcha():
    """Extracts and solves the captcha question."""
    try:
        captcha_text = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'What is')]"))
        ).text
        numbers = re.findall(r'\d+', captcha_text)
        return str(sum(map(int, numbers)))
    except Exception as e:
        print("Error solving captcha:", e)
        return ""

def is_normal_page():
    try:
        body_class = driver.find_element(By.TAG_NAME, "body").get_attribute("class")
        return "frontpage" in body_class
    except:
        return False

def fetch_pan_details(pan_number):
    try:
        pan_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "pan")))
        pan_input.send_keys(str(pan_number))
        
        captcha_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "captcha")))
        captcha_answer = solve_captcha()
        captcha_input.send_keys(captcha_answer)
        
        search_button = driver.find_element(By.XPATH, "//button[contains(text(),'Search')]")
        search_button.click()

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Office')]")))
        
        details = {"PAN": pan_number}
        fields = {
            "Office": "Office",
            "Name": "Name",
            "Telephone": "Telephone",
            "Ward": "Ward",
            "Street Name": "Street Name",
            "City Name": "City Name",
            "Income Tax": "Income Tax",
            "VAT": "VAT",
            "VAT Filing Period": "VAT Filing Period",
            "Fiscal Year / Return Verified Date": "Fiscal Year / Return Verified Date"
        }
        
        for key, field in fields.items():
            try:
                details[key] = driver.find_element(By.XPATH, f"//td[contains(text(),'{field}')]/following-sibling::td").text
            except:
                details[key] = "#NA"

        try:
            details["Non-filer:"] = driver.find_element(By.XPATH, "//td[contains(text(),'Income Tax')]/following-sibling::td[2]").text
        except:
            details["Non-filer:"] = "#NA"

        try:
            details["Non-filer since"] = driver.find_element(By.XPATH, "//td[contains(text(),'VAT')]/following-sibling::td[2]").text
        except:
            details["Non-filer since"] = "#NA"

        return details
    
    except Exception as e:
        print(f"Error processing PAN {pan_number}: {e}")
        return {"PAN": pan_number, "Error": "Failed to fetch data"}

# Fetch details for each PAN
results = []
for pan in df['PAN']:
    while True:
        driver.get("https://ird.gov.np/pan-search")

        if not is_normal_page():
            print(f"PAN {pan} - captcha page detected, retrying in 10s...")
            time.sleep(10)
            continue

        # Normal page, scrape details
        details = fetch_pan_details(pan)
        results.append(details)
        print(f"Processed PAN: {pan}")
        time.sleep(1)
        break 

# Save results to Excel
output_df = pd.DataFrame(results)
output_df.to_excel("pan_results.xlsx", index=False, engine='openpyxl')

driver.quit()
print("Data extraction complete. Results saved in 'pan_results.xlsx'")
