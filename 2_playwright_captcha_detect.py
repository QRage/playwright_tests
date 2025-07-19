import asyncio
from playwright.async_api import async_playwright


async def try_recaptcha_v2(url):
    """
    Attempts to bypass Google reCAPTCHA v2 (checkbox) at the given URL
    using Playwright without side API.

    Args:
    url (str): URL of the Google reCAPTCHA v2 test page.
    Example: 'https://www.google.com/recaptcha/api2/demo'

    Returns:
    bool: True if the bypass was successful, False otherwise.
    """
    success = False
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until='domcontentloaded')
            print('page ready')

            recaptcha_iframe = page.frame_locator('iframe[title="reCAPTCHA"]')

            if recaptcha_iframe:
                print('captcha found')
                
                await recaptcha_iframe.locator('#recaptcha-anchor').click(timeout=10000)

                await asyncio.sleep(3)

                try:
                    is_checked = await recaptcha_iframe.locator('#recaptcha-anchor').get_attribute('aria-checked')
                    if is_checked == 'true':
                        print('reCAPTCHA bypassed')
                        success = True
                    else:
                        print('reCAPTCHA failed')
                except Exception:
                    print('Unavailable to get checkbox state. Maybe visual check has appeared.')

            else:
                print('no iframe reCAPTCHA found')
        
        except Exception as e:
            print('An error occured:\n{e}')
        finally:
            await browser.close()

    return success


test_recaptcha_url = 'https://www.google.com/recaptcha/api2/demo'


if __name__ == '__main__':
    result = asyncio.run(try_recaptcha_v2(test_recaptcha_url))
    if result:
        print('Success!')
    else:
        print('Failed!')
