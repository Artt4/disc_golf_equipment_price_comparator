import sys
import os
import hashlib
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def get_rendered_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        try:
            print(f"Visiting: {url}")
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle", timeout=5000)  # Wait for all requests
            page.wait_for_selector("article.productitem", timeout=5000)  # wait for content
        except PlaywrightTimeout:
            print(f"Timeout waiting for product cards on {url}")
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
        html = page.content()
        browser.close()
        return html

def get_data_discking():
    current_directory = os.path.dirname(os.path.realpath(__file__))
    app_directory = os.path.abspath(os.path.join(current_directory, '..', '..'))
    sys.path.append(app_directory)
    
    from handle_db_connections import create_conn

    url_placeholder = 1

    while True:
        all_products = []
        print("getting discking page")

        page_url = f"https://kiekkokingi.fi/collections/uudet-frisbeegolfkiekot?page={url_placeholder}&grid_list=grid-view"

        # Get rendered HTML using Selenium
        html_content = get_rendered_html(page_url)
        soup = BeautifulSoup(html_content, 'html.parser')

        ############################################################################################

        products = soup.find_all('article', class_='productitem')
        if not products:
            print(f"No products found on page {url_placeholder}. Scraping finished.")
            break

        if products == []:
            break

        for product in products:

            title = product.find('h2', class_='productitem--title').get_text(strip=True)

            price_element = product.find_all('span', class_='money')
            if len(price_element) > 1:
                price_element = price_element[1].get_text(strip=True).replace(' ', '')
            else: 
                price_element = price_element[0].get_text(strip=True).replace(' ', '')
            numeric_value = ''.join([char for char in price_element if char.isdigit() or char == ',' or char == '.']).replace(',', '.')
            currency_symbol = ''.join([char for char in price_element if not char.isdigit() and char != ',' and char != '.']).strip()
            numeric_amount = float(numeric_value)
                        
            flight_ratings = {}
            flight_ratings_list = product.find_all('div', class_='tooltip')
            flight_ratings['Speed'] = flight_ratings_list[0].contents[0].strip() if len(flight_ratings_list) > 0 else None
            flight_ratings['Glide'] = flight_ratings_list[1].contents[0].strip() if len(flight_ratings_list) > 0 else None
            flight_ratings['Turn'] = flight_ratings_list[2].contents[0].strip() if len(flight_ratings_list) > 0 else None
            flight_ratings['Fade'] = flight_ratings_list[3].contents[0].strip() if len(flight_ratings_list) > 0 else None  

            link_to_disc_element = product.find('a', class_='productitem--image-link')
            link_to_disc = link_to_disc_element['href'] if link_to_disc_element else 'No link found'

            image_element = product.find('img', class_='productitem--image-primary')
            image_url = image_element['src'] if image_element else 'No image found'

            result = {
                'title': title,
                'price': numeric_amount,
                'currency': currency_symbol,
                'flight_ratings': flight_ratings,
                'link_to_disc': "https://kiekkokingi.fi/" + link_to_disc,
                'image_url': image_url,
                'store': "kiekkokingi.fi"
            }

            combined = f"{result.get('title')}_{result.get('store')}"
            combined = combined.lower().replace(' ', '')
            unique_id = hashlib.sha256(combined.encode()).hexdigest()

            result["unique_id"] = unique_id

            all_products.append(result)

        url_placeholder = url_placeholder + 1

        ############################################################################################

        connection = create_conn()

        try:

            with connection.cursor() as cursor:

                sql = """
                INSERT INTO product_table (unique_id, title, price, currency, speed, glide, turn, fade, link_to_disc, image_url, store)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                unique_id = VALUES(unique_id),
                price = VALUES(price),
                currency = VALUES(currency),
                speed = VALUES(speed),
                glide = VALUES(glide),
                turn = VALUES(turn),
                fade = VALUES(fade),
                link_to_disc = VALUES(link_to_disc),
                image_url = VALUES(image_url);
                """
                
                data = [
                    (
                        product['unique_id'],
                        product['title'],
                        product['price'],
                        product['currency'],
                        product['flight_ratings']['Speed'],
                        product['flight_ratings']['Glide'],
                        product['flight_ratings']['Turn'],
                        product['flight_ratings']['Fade'],
                        product['link_to_disc'],
                        product['image_url'],
                        product['store']
                    )
                    for product in all_products
                ]

                cursor.executemany(sql, data)
                connection.commit()

        finally:

            connection.close()

if __name__ == "__main__":
    get_data_discking()