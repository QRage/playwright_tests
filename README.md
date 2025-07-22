##  Description
This repository serves as a personal learning environment dedicated to exploring Playwright and Playwright Stealth. Having previously worked with established web automation tools like 🥣 Beautiful Soup and 🧪 Selenium (whose development began around 2004), I aim to delve into Playwright, a more modern library, based on recommendations from the developer community. This initiative is designed to familiarize myself with its capabilities and advantages in contemporary web automation and scraping.

### 🛠️ 1_playwright_scraper.py
This script demonstrates basic web scraping functionality using Playwright. It's designed to extract content from a documentation website. You can easily modify the target URL to scrape other publicly accessible documentation or simple web pages. This script does not incorporate "stealth" techniques, as the target website is assumed to have no CAPTCHA or advanced bot detection mechanisms.

### 🛠️ 2_playwright_captcha_detect.py
This script attempts to detect and interact with a CAPTCHA on a web page. Its primary goal is to bypass the CAPTCHA if it's a simple checkbox (e.g., reCAPTCHA v2 without a visual puzzle). As noted, this script will return False if a visual puzzle appears, indicating that a more advanced solution is required. This serves as a precursor to addressing complex CAPTCHA challenges.

### 🛠️ 3_playwright_stealth_bypass.py
This script builds upon the previous attempts by integrating playwright-stealth and a CAPTCHA-solving service (2Captcha) to bypass reCAPTCHA v2. It aims to demonstrate how to:
* Apply stealth techniques to make the automated browser less detectable.
* Utilize a third-party CAPTCHA solving service to obtain a valid CAPTCHA token.
* Inject the solved token back into the web page to successfully pass the reCAPTCHA challenge, even when a visual puzzle is presented.
