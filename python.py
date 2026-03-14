import requests
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE  = "pan.xlsx"
OUTPUT_FILE = "pan_results.xlsx"
API_URL     = "https://ird.gov.np/api/getPanSearch/"
PAGE_URL    = "https://ird.gov.np/pan-search/"
HEADERS     = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer"   : PAGE_URL,
    "Origin"    : "https://ird.gov.np",
}
DELAY = 1

ACCT_TYPE_MAP     = {"10": "Income Tax", "20": "VAT", "30": "Excise", "40": "TDS", "50": "Education Tax"}
FILING_PERIOD_MAP = {"T": "Trimester", "Y": "Yearly", "M": "Monthly"}
STATUS_MAP        = {"A": "Active", "I": "Inactive"}
CLEARANCE_MAP     = {"Y": "Cleared", "N": "Not Cleared"}

if not os.path.exists(INPUT_FILE):
    print(f"Error: File '{INPUT_FILE}' not found!")
    exit()

df = pd.read_excel(INPUT_FILE, engine="openpyxl")
df.columns = df.columns.str.strip()

if "PAN" not in df.columns:
    print(f"Error: 'PAN' column not found! Available columns: {df.columns.tolist()}")
    exit()

driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msedgedriver.exe")
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Edge(service=Service(driver_path), options=options)


def get_recaptcha_token(pan_number):
    driver.get(PAGE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "pan"))
    ).send_keys(str(pan_number))
    driver.find_element(By.ID, "submit").click()
    for _ in range(30):
        token = driver.execute_script("return document.getElementById('g-recaptcha-response').value;")
        if token:
            return token
        time.sleep(1)
    raise Exception(f"reCAPTCHA timed out for PAN {pan_number}")


def fetch_pan_details(pan_number):
    try:
        token   = get_recaptcha_token(pan_number)
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        csrf    = cookies.get("csrftoken")
        if not csrf:
            raise Exception("CSRF token missing")

        response = requests.post(
            API_URL,
            files={"pan": (None, str(pan_number)), "g-recaptcha-response": (None, token)},
            headers={**HEADERS, "X-CSRFToken": csrf},
            cookies=cookies,
        )
        data = response.json()

        if data.get("code") != 1 or not data.get("data"):
            return {"PAN": pan_number, "Error": "Failed to fetch data"}

        d             = data["data"]
        pan_info      = d.get("panDetails",            [{}])[0]
        business      = d.get("businessDetail",        [{}])[0]
        tax_clearance = d.get("panTaxClearance",       [{}])[0]
        reg_types     = {
            ACCT_TYPE_MAP.get(str(r["acctType"]), f"Type {r['acctType']}"): r
            for r in d.get("panRegistrationDetail", [])
        }

        it  = reg_types.get("Income Tax",    {})
        vat = reg_types.get("VAT",           {})
        edu = reg_types.get("Education Tax", {})

        city   = pan_info.get("vdc_Town",    "") or ""
        street = pan_info.get("street_Name", "") or ""

        return {
            "PAN"                            : pan_number,
            "Office"                         : pan_info.get("office_Name") or "#NA",
            "Name"                           : business.get("trade_Name_Eng") or "#NA",
            "Telephone"                      : pan_info.get("telephone") or "#NA",
            "Ward"                           : pan_info.get("ward_No") or "#NA",
            "Street Name"                    : street or "#NA",
            "City Name"                      : city or "#NA",
            "Income Tax"                     : STATUS_MAP.get(it.get("accountStatus", ""), "#NA"),
            "VAT"                            : STATUS_MAP.get(vat.get("accountStatus", "") or edu.get("accountStatus", ""), "#NA"),
            "VAT Filing Period"              : FILING_PERIOD_MAP.get(vat.get("filing_Period", "") or edu.get("filing_Period", ""), "#NA"),
            "Fiscal Year / Return Verified Date": f"{tax_clearance.get('fiscal_Year', '#NA')} / {tax_clearance.get('return_Verified_Date', '#NA')}",
            "Non-filer:"                     : pan_info.get("unfiled_Returns") or "#NA",
            "Non-filer since"                : "#NA",
        }

    except Exception as e:
        print(f"Error processing PAN {pan_number}: {e}")
        return {"PAN": pan_number, "Error": "Failed to fetch data"}


results = []
total   = len(df["PAN"])
print(f"Processing {total} PAN(s)...\n")

for i, pan in enumerate(df["PAN"], 1):
    print(f"[{i}/{total}] {pan}")
    details = fetch_pan_details(pan)
    results.append(details)
    print(f"  -> {details.get('Name', details.get('Error', 'N/A'))}")
    time.sleep(DELAY)

pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
driver.quit()
print(f"\nDone. {len(results)} record(s) saved to '{OUTPUT_FILE}'")