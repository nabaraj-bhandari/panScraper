# PAN Scraper

Fetches PAN details from [IRD Nepal](https://ird.gov.np/pan-search) and saves them to Excel. Runs headless on Windows.

---

## Files
```
python.py          # Main script
pan.xlsx           # Input — must have a column named 'PAN'
pan_results.xlsx   # Output — generated after running
requirements.txt   # Dependencies
msedgedriver.exe   # Edge WebDriver (see setup)
```

---

## Setup

**1. Install Python 3.8+**
[python.org/downloads](https://www.python.org/downloads/)

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Download Edge WebDriver**
- Check your Edge version: `Settings → Help & feedback → About Microsoft Edge`
- Download the matching driver: [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- Place `msedgedriver.exe` in the same folder as `python.py`

**4. Prepare input file**
`pan.xlsx` must have a column named `PAN`:

| PAN       |
|-----------|
| 123456789 |
| 987654321 |

**5. Run**
```bash
python python.py
```

Results are saved to `pan_results.xlsx`.

---

## Notes

- WebDriver version must match your Edge browser version exactly.
- The script uses the IRD API directly — reCAPTCHA is solved automatically via the browser.
- Failed PANs are written to the output with an `Error` column instead of stopping the run.