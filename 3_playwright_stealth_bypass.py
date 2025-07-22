import asyncio
import os
import concurrent.futures

from playwright.async_api import async_playwright
from playwright_stealth.stealth import Stealth 
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv


load_dotenv()
TWO_CAPTCHA_API_KEY = os.getenv('TWO_CAPTCHA_API_KEY')

if not TWO_CAPTCHA_API_KEY:
    print('Error: API key for 2Captcha not found. Make sure it is set in your .env file as TWO_CAPTCHA_API_KEY.')
    raise ValueError("TWO_CAPTCHA_API_KEY is not set in .env file.")

solver = TwoCaptcha(TWO_CAPTCHA_API_KEY)

TEST_RECAPTCHA_URL = 'https://www.google.com/recaptcha/api2/demo'

def _get_captcha_result_sync(s, sitekey, url):
    """
    Synchronous call to the recaptcha method from the twocaptcha library.
    This function will be executed in a separate thread via ThreadPoolExecutor.
    """
    return s.recaptcha(sitekey=sitekey, url=url)

async def solve_recaptcha_v2(page, current_url, sitekey, executor):
    """
    Solves reCAPTCHA v2 using 2Captcha (synchronous client) and inserts the token into the page.
    Uses ThreadPoolExecutor for asynchronous execution of synchronous code.
    
    Args:
        page: Playwright Page object.
        current_url (str): Current URL of the page where reCAPTCHA is located.
        sitekey (str): reCAPTCHA sitekey found on the page.
        executor (concurrent.futures.ThreadPoolExecutor): Thread pool for executing synchronous operations.
    Returns:
        bool: True if the solution was successful and the token was inserted, False otherwise.
    """
    try:
        print(f"Trying to solve reCAPTCHA v2 for URL: {current_url}")
        
        loop = asyncio.get_running_loop()

        result_future = loop.run_in_executor(
            executor,
            _get_captcha_result_sync,
            solver,
            sitekey,
            current_url
        )
        
        result = await result_future

        # print(f"DEBUG: Type of result (after await): {type(result)}")
        # print(f"DEBUG: Result content: {result}")

        if result and 'code' in result:
            captcha_token = result['code']
            print(f"2Captcha has solved reCAPTCHA v2, token: {captcha_token[:30]}...")

            await page.evaluate(
                f'document.querySelector("#g-recaptcha-response").innerHTML = "{captcha_token}";'
            )

            try:
                await page.evaluate(
                    'window.onSuccess(arguments[0]);', captcha_token)
                print('reCAPTCHA v2 solved successfully.')
            except Exception as e:
                print(f'Error executing onSuccess callback: {e}')
            
            await asyncio.sleep(2) 

            verify_button = page.locator('#recaptcha-demo-submit')
            if await verify_button.is_enabled():
                print('Sumbit button is enabled, clicking it. Probably reCAPTCHA v2 solved.')
                return True
            else:
                print('Button submit is not enabled, reCAPTCHA v2 not solved.')
                return False

        else:
            print(f'2Captcha could not solve reCAPTCHA v2 for {current_url} or returned unexpected format.')
            return False

    except Exception as e:
        print(f'Error solving reCAPTCHA v2: {e}')
        return False

async def try_recaptcha_v2_with_2captcha(url):
    """
    Attempts to bypass Google reCAPTCHA v2 (checkbox) at the given URL
    using Playwright with 2Captcha service.
    Args:
        url (str): URL of the Google reCAPTCHA v2 test page.
        Example: 'https://www.google.com/recaptcha/api2/demo'
        Returns:
        bool: True if the bypass was successful, False otherwise.
    Returns:
        bool: True if the reCAPTCHA v2 was solved successfully, False otherwise.
    """
    success = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        stealth = Stealth()
        stealth.apply_stealth_sync(page) 
        print("Playwright Stealth applied.")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                await page.goto(url, wait_until='domcontentloaded')
                print(f'Page loaded: {url}')

                recaptcha_iframe_locator = page.frame_locator('iframe[title="reCAPTCHA"]')
                if not recaptcha_iframe_locator:
                    print('reCAPTCHA iframe not found.')
                    return False
                print('reCAPTCHA iframe found, trying to solve it.')

                sitekey_element = await page.locator('.g-recaptcha').get_attribute('data-sitekey')
                if not sitekey_element:
                    print('Unable to find reCAPTCHA sitekey on the page.')
                    return False
                
                success = await solve_recaptcha_v2(page, url, sitekey_element, executor)

                if success:
                    print('reCaptcha v2 solved successfully.')
                    await page.locator('#recaptcha-demo-submit').click()
                    print('Button "submit" clicked.')
                    await asyncio.sleep(5) 

                    success_message_locator = page.locator('.recaptcha-success')
                    if await success_message_locator.is_visible():
                        print('reCAPTCHA v2 bypass message appeared.')
                        return True
                    else:
                        print('reCAPTCHA v2 bypass message did not appear.')
                        return False
                    
                else:
                    print('Failed to bypass reCAPTCHA v2.')
                    return False
                
            except Exception as e:
                print(f'An error occurred: {e}')
            finally:
                await browser.close()
                print('Browser closed.')

    return success


if __name__ == '__main__':
    if not TWO_CAPTCHA_API_KEY:
        print('Please set the TWO_CAPTCHA_API_KEY in the .env file.')
    else:
        print(f'Starting reCAPTCHA v2 bypass test with 2Captcha at {TEST_RECAPTCHA_URL}')
        final_result = asyncio.run(try_recaptcha_v2_with_2captcha(TEST_RECAPTCHA_URL))
        if final_result:
            print('Success! reCAPTCHA v2 bypassed.')
        else:
            print('Failed to bypass reCAPTCHA v2.')
