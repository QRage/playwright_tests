import asyncio
from playwright.async_api import async_playwright


async def scrape_python_docs(url):
    """
    Asynchronously scrapes the specified URL to extract the page title,
    all links, and the main text content.

    This function uses Playwright to automate the Chromium browser
    and navigate to the specified URL. It extracts the following data:
    - The page title.
    - A list of all links (text and URL).
    - The main text content from the specified div element.

    Args:
    url (str): The URL of the web page to scrape.

    Returns:
    None: The function prints the extracted data to the console.
    Can be extended to return structured data.

    Raises:
    Exception: If an error occurs during navigation or scraping.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until='domcontentloaded')

            title = await page.title()
            print("Page title: {title}")

            links_elements = await page.query_selector_all('a')
            all_links = []
            for link_element in links_elements:
                href = await link_element.get_attribute('href')
                text = await link_element.text_content()
                if href:
                    all_links.append({"text": text.strip(), "href": href})

            print(f'Links found: {len(all_links)}')

            for i, link in enumerate(all_links[:5]):
                print(f'{i+1}. Text: "{link['text']}", URL: "{link["href"]}"')

            content_div = await page.query_selector('div.body')
            if content_div:
                main_content_text = await content_div.text_content()
                print(f'\nMain content (cut):\n{main_content_text[:500]}...')
            else:
                print('No content found.')

        except Exception as e:
            print(f'Error occured while scrapping:\n{e}')
        finally:
            await browser.close()


target_url = "https://docs.python.org/3/"


if __name__ == "__main__":
    asyncio.run(scrape_python_docs(target_url))
