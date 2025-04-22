from playwright.sync_api import sync_playwright
import json
import time
import os

EMAIL = "saniyanasir786@gmail.com"
PASSWORD = "N8uY6u4X"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Login
        page.goto("https://hiring.idenhq.com/")
        page.fill('input[type="email"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # 2. Navigate to Challenge and Product Inventory
        page.click("text=Launch Challenge")
        page.wait_for_selector("text=Welcome to the Admin Panel")
        page.click("button:has-text('Dashboard')")
        page.click("text=Inventory")
        page.click("text=Products")
        page.click("text=Full Catalog")

        # 3. Wait for product cards to load
        try:
            page.wait_for_selector("div.grid > div", timeout=60000)
        except Exception as e:
            print(f"Error waiting for product cards: {e}")
            return

        # 4. Scroll to load all cards (up to 50 scrolls)
        SCROLL_CONTAINER = "div.grid"
        prev_count = -1
        max_scrolls = 50

        for _ in range(max_scrolls):
            cards = page.query_selector_all("div.grid > div")
            current_count = len(cards)
            print(f"Loaded: {current_count} cards")

            if current_count == prev_count:
                break
            prev_count = current_count

            page.evaluate(f'''
                document.querySelector("{SCROLL_CONTAINER}").scrollBy(0, 2000);
            ''')
            time.sleep(1.2)

        # 5. Extract product data from each card
        product_cards = page.query_selector_all("div.grid > div")

        products = []
        for card in product_cards:
            try:
                title = card.query_selector("h6") or card.query_selector("h5")
                weight_label = card.query_selector("text=Weight (kg)")
                desc_label = card.query_selector("text=Description")
                price_label = card.query_selector("text=Price")

                # Get next sibling text nodes
                weight = weight_label.evaluate_handle("el => el.nextSibling?.textContent") if weight_label else ""
                desc = desc_label.evaluate_handle("el => el.nextSibling?.textContent") if desc_label else ""
                price = price_label.evaluate_handle("el => el.nextSibling?.textContent") if price_label else ""

                product = {
                    "title": title.inner_text().strip() if title else "",
                    "weight": weight.json_value().strip() if weight else "",
                    "description": desc.json_value().strip() if desc else "",
                    "price": price.json_value().strip() if price else ""
                }

                products.append(product)
            except Exception as e:
                print(f"❌ Error parsing a card: {e}")

        # 6. Save data to products.json
        if products:
            file_path = "products.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(products, f, indent=2)
            print(f"✅ Saved {len(products)} products to '{file_path}'")
        else:
            print("⚠️ No products extracted!")

        browser.close()

run()
