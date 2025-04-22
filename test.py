from playwright.sync_api import sync_playwright
import json

EMAIL = "your@email.com"
PASSWORD = "your_password"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Open login page
        page.goto("https://your-website-url.com/login")  # Replace with real URL

        # 2. Fill credentials and login
        page.fill('input[type="email"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)
        page.click('button[type="submit"]')  # Adjust selector if needed

        page.wait_for_load_state("networkidle")

        # 3. Navigate the breadcrumbs
        page.click("text=Dashboard")
        page.click("text=Inventory")
        page.click("text=Products")
        page.click("text=Full Catalog")

        # 4. Extract data from the table
        products = []
        while True:
            rows = page.query_selector_all("table tbody tr")
            for row in rows:
                cells = row.query_selector_all("td")
                product = [cell.inner_text().strip() for cell in cells]
                products.append(product)

            next_btn = page.query_selector('text=Next')
            if next_btn and next_btn.is_enabled():
                next_btn.click()
                page.wait_for_timeout(1000)
            else:
                break

        # 5. Save to JSON file
        with open("products.json", "w") as f:
            json.dump(products, f, indent=2)

        browser.close()

run()
