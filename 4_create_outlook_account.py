import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def outlook_start(url: str):
    """
    Method to create an Outlook account using Playwright.
    This function navigates to the Outlook sign-up page, fills in the required fields,
    and handles CAPTCHA challenges if they appear.
    It uses Playwright for browser automation and stealth techniques to avoid detection.

    :param url: URL of the Outlook sign-up page.
    :return: True if account creation is successful, False otherwise.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        try:
            await page.goto(url, wait_until='domcontentloaded')

            sign_in_button = page.locator('#c-shellmenu_custom_outline_signin_bhvr100_right')
            await sign_in_button.wait_for(state='visible', timeout=15000)
            await sign_in_button.click()

            await page.wait_for_load_state('networkidle', timeout=15000)
            sign_up_id = page.locator('#signup')
            await sign_up_id.wait_for(state='visible', timeout=15000)
            await sign_up_id.click()

            await page.wait_for_load_state('networkidle', timeout=15000)
            await asyncio.sleep(2)
            input_email_name_field_id = page.locator('#floatingLabelInput6')
            await input_email_name_field_id.wait_for(state='visible', timeout=15000)
            await input_email_name_field_id.fill('georgetestman19991')
            next_button = page.locator('button[data-testid="primaryButton"]')
            await next_button.wait_for(state='visible', timeout=15000)
            await next_button.click()

            random_password = 'TestPassword123!'
            password_input_field = page.locator('[autocomplete="new-password"]')

            await password_input_field.wait_for(state='visible', timeout=15000)
            await password_input_field.fill(random_password)
            await next_button.wait_for(state='visible', timeout=15000)
            await next_button.click()

            month_dropdown_button = page.locator('[aria-label="Birth month"]')
            await month_dropdown_button.wait_for(state='visible', timeout=15000)
            box_month = await month_dropdown_button.bounding_box()
            if box_month:
                center_x = box_month['x'] + box_month['width'] / 2
                center_y = box_month['y'] + box_month['height'] / 2
                await page.mouse.click(center_x, center_y)
            else:
                await month_dropdown_button.click()
            month_name = 'May'
            month_option = page.get_by_role('option', name=month_name, exact=True)
            await month_option.wait_for(state='visible', timeout=15000)
            await month_option.click()
            
            await asyncio.sleep(1)
            day_dropdown_button = page.locator('[aria-label="Birth day"]')
            await day_dropdown_button.wait_for(state='visible', timeout=15000)
            box_day = await day_dropdown_button.bounding_box()
            if box_day:
                center_x = box_day['x'] + box_day['width'] / 2
                center_y = box_day['y'] + box_day['height'] / 2
                await page.mouse.click(center_x, center_y)
            else:
                await day_dropdown_button.click()
            day_number = '15'
            day_option = page.get_by_role('option', name=day_number, exact=True)
            await day_option.wait_for(state='visible', timeout=15000)
            await day_option.click()

            year_input_field = page.get_by_label('Birth year').or_(page.locator('[name="BirthYear"]'))
            await year_input_field.wait_for(state='visible', timeout=15000)
            await year_input_field.fill('1991')

            await next_button.wait_for(state='visible', timeout=15000)
            await next_button.click()

            first_name = 'George'
            last_name = 'McTest'
            first_name_input = page.locator('#firstNameInput')
            last_name_input = page.locator('#lastNameInput')
            await first_name_input.wait_for(state='visible', timeout=15000)
            await first_name_input.fill(first_name)
            await last_name_input.wait_for(state='visible', timeout=15000)
            await last_name_input.fill(last_name)
            await next_button.wait_for(state='visible', timeout=15000)
            await next_button.click()
            
            await asyncio.sleep(7)

            check_for_detection_message = page.get_by_text("We can't create your account", exact=True)
            if await check_for_detection_message.is_visible(timeout=5000):
                print("Account creation detected as suspicious. Try to use a different IP address or browser profile.")
                await browser.close()
                return False

            is_captcha_present = await page.locator('div[aria-label="Press & Hold Human Challenge"]').is_visible()
            if is_captcha_present:
                captcha_solved = await solve_press_and_hold_captcha(page, hold_duration_seconds=7)
                if captcha_solved:
                    print("CAPTCHA 'Press & Hold' successfully solved.")
                else:
                    print("Captcha 'Press & Hold' not solved.")

        except Exception as e:
            print(f'An error occurred while navigating to {url}: {e}')
            await browser.close()
            return False

        await page.wait_for_timeout(5000)
        await browser.close()
        return True
    

async def solve_press_and_hold_captcha(page, hold_duration_seconds: int = 7):
    """
    Method to solve the 'Press & Hold' CAPTCHA challenge.
    This function simulates a mouse press and hold action on the CAPTCHA button.
    It waits for the button to become visible, calculates its center position,
    and performs the hold action for the specified duration.
    It returns True if the CAPTCHA is solved successfully, otherwise False.
    
    :param page: Playwright page object.
    :param hold_duration_seconds: Duration to hold the mouse down in seconds.
    :return: True if CAPTCHA is solved, False otherwise.
    """
    captcha_button = page.get_by_label('Press & Hold Human Challenge')
    try:
        await captcha_button.wait_for(state='visible', timeout=15000)

        box = await captcha_button.bounding_box()
        if not box:
            return False

        center_x = box['x'] + box['width'] / 2
        center_y = box['y'] + box['height'] / 2

        await page.mouse.move(center_x, center_y)
        await page.mouse.down()
        await asyncio.sleep(hold_duration_seconds)
        await page.mouse.up()

        await captcha_button.wait_for(state='hidden', timeout=10000)
        return True

    except Exception as e:
        print(f"Error while solving CAPTCHA 'Press & Hold': {e}")
        return False


if __name__ == '__main__':
    test_url = 'https://outlook.live.com/owa/'
    asyncio.run(outlook_start(test_url))
