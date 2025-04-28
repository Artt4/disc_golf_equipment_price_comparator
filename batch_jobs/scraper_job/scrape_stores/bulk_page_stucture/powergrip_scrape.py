from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import sys, os, time, hashlib
from bs4 import BeautifulSoup
from datetime import datetime
from handle_db_connections import create_conn

def get_data_powergrip_from_bulk():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Opening Powergrip main page...")
        page.goto("https://powergrip.fi/tuote/", timeout=15000)

        try:
            page.wait_for_selector("div.ais-infinite-hits--item.product-thumbnail-wrapper", timeout=6000)
        except PlaywrightTimeout:
            print("Timeout: No products found on initial load.")
            return

        seen_ids = set()
        connection = create_conn()

        while True:
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            product_cards = soup.select("div.ais-infinite-hits--item.product-thumbnail-wrapper")

            print(f"Parsing {len(product_cards)} product cards...")

            new_products = []
            for i, card in enumerate(product_cards):
                try:
                    title_el = card.select_one(".product-title span")
                    if not title_el:
                        continue
                    title = title_el.get_text(strip=True)

                    price_el = card.select_one(".price-tag")
                    if not price_el:
                        continue
                    price_text = price_el.get_text(strip=True).replace(" ", "")
                    numeric_value = ''.join(c for c in price_text if c.isdigit() or c in ',.')
                    currency_symbol = "€"

                    if not numeric_value:
                        continue

                    combined = f"{title}_powergrip.fi".lower().replace(" ", "")
                    product_id = hashlib.sha256(combined.encode()).hexdigest()
                    if product_id in seen_ids:
                        continue
                    seen_ids.add(product_id)

                    ratings = {"Speed": None, "Glide": None, "Turn": None, "Fade": None}
                    ratings_div = card.select_one(".product-flight-ratings")
                    if ratings_div:
                        label_map = {"SPEED": "Speed", "GLIDE": "Glide", "TURN": "Turn", "FADE": "Fade"}
                        for li in ratings_div.select("li"):
                            label = li.select_one(".label")
                            value = li.select_one(".value")
                            if label and value:
                                key = label_map.get(label.text.strip().upper(), label.text.strip())
                                try:
                                    ratings[key] = float(value.text.strip().replace(",", "."))
                                except:
                                    pass

                    if any(r is None for r in ratings.values()):
                        continue

                    img_el = card.select_one("img")
                    image_url = img_el["src"] if img_el else None

                    link_el = card.select_one("a")
                    link_to_disc = f"https://powergrip.fi{link_el['href']}" if link_el and link_el.has_attr("href") else None

                    product = {
                        "unique_id": product_id,
                        "title": title,
                        "price": numeric_value,
                        "currency": currency_symbol,
                        "flight_ratings": ratings,
                        "link_to_disc": link_to_disc,
                        "image_url": image_url,
                        "store": "powergrip.fi"
                    }

                    with connection.cursor() as cursor:
                        sql = """
                        INSERT INTO product_table (unique_id, title, price, currency, speed, glide, turn, fade, link_to_disc, image_url, store)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        price = VALUES(price), currency = VALUES(currency), speed = VALUES(speed),
                        glide = VALUES(glide), turn = VALUES(turn), fade = VALUES(fade),
                        link_to_disc = VALUES(link_to_disc), image_url = VALUES(image_url);
                        """
                        cursor.execute(sql, (
                            product["unique_id"], product["title"], product["price"], product["currency"],
                            product["flight_ratings"]["Speed"], product["flight_ratings"]["Glide"],
                            product["flight_ratings"]["Turn"], product["flight_ratings"]["Fade"],
                            product["link_to_disc"], product["image_url"], product["store"]
                        ))
                        connection.commit()

                    new_products.append(product)

                except Exception as e:
                    print(f"Error parsing product card: {e}")


            try:
                page.wait_for_selector(".ais-infinite-hits--showmoreButton", state="visible")
                page.dispatch_event(".ais-infinite-hits--showmoreButton", "click")
                page.wait_for_selector(
                    ".ais-infinite-hits--item.product-thumbnail-wrapper:nth-child({})".format(len(product_cards) + 1),
                    timeout=4000
                )
                page.wait_for_timeout(500)
            except PlaywrightTimeout:
                break

        connection.close()
        browser.close()

if __name__ == "__main__":
    get_data_powergrip_from_bulk()
