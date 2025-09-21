# PAN Scraper

A Python script to scrape **PAN details** from [IRD Nepal](https://ird.gov.np/pan-search).
Works on **Windows** and **Linux**, runs **headless**, and automatically retries when a captcha appears.

---

## Repository Files

```
python.py          # Main script
pan.xlsx           # Input file containing PAN numbers (must have a column named 'PAN')
pan_results.xlsx   # Output file with scraped results
requirements.txt   # Python dependencies
```

---

## Setup

### 1. Install Python

Requires **Python 3.8+**
[Download Python](https://www.python.org/downloads/)

---

### 2. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

---

### 3. Download WebDriver

1. Check your **Edge browser version** (Settings → About → Version).
2. Download the matching **Edge WebDriver** from:
   [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH#downloads)
3. Place the downloaded file in the same folder as `python.py`:

   * **Windows:** `msedgedriver.exe`
   * **Linux:** `msedgedriver`

---

### 4. Prepare Input File

Your `pan.xlsx` must contain a column named **`PAN`**:

| PAN       |
| --------- |
| 123456789 |
| 987654321 |

---

### 5. Run the Script

Navigate to the folder and run:

```bash
python python.py
```

The results will be saved in **`pan_results.xlsx`**.

---

## Notes

* WebDriver version **must match** your Edge browser version.
* If captcha appears, the script **waits 10 seconds and retries automatically**.
* If no `PAN` column is found, the script will exit with an error.

