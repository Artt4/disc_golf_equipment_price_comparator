import sys
import os
import requests
import hashlib

from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

current_directory = os.path.dirname(os.path.realpath(__file__))
app_directory = os.path.abspath(os.path.join(current_directory, '..', '..'))
sys.path.append(app_directory)

from handle_db_connections import create_conn

def get_data_discsport():

    all_products = []

    url_placeholders = ["putters", "midrange", "distance-drivers"]

    for url_placeholder in url_placeholders:

        print("getting discsport page")

        page_url = f"https://www.innovaeurope.com/en/{url_placeholder}/results,1-400"

        response = requests.get(page_url)

        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        ############################################################################################

        products = soup.find_all('div', class_='product product-grid-view col-6 col-sm-6 col-md-4 col-lg-3')

        for product in products:

            title = product.find('h3', class_='product-name text-center m-0 mb-2').get_text(strip=True)

            price_element = product.find('span', class_='PricesalesPrice').get_text(strip=True).replace(' ', '')
            numeric_value = ''.join([char for char in price_element if char.isdigit() or char == ',' or char == '.'])
            currency_symbol = ''.join([char for char in price_element if not char.isdigit() and char != ',' and char != '.'])
            amount = float(numeric_value.replace(",", "."))

            flight_ratings = {}
            speed_tag = product.find('a', class_='flight-speed')
            flight_ratings['Speed'] = speed_tag.find('span').get_text(strip=True) if speed_tag and speed_tag.find('span') else None
            glide_tag = product.find('a', class_='flight-glide')
            flight_ratings['Glide'] = glide_tag.find('span').get_text(strip=True) if glide_tag and glide_tag.find('span') else None
            turn_tag = product.find('a', class_='flight-turn')
            flight_ratings['Turn'] = turn_tag.find('span').get_text(strip=True) if turn_tag and turn_tag.find('span') else None
            fade_tag = product.find('a', class_='flight-fade')
            flight_ratings['Fade'] = fade_tag.find('span').get_text(strip=True) if fade_tag and fade_tag.find('span') else None

            link_to_disc_element = product.find('a')
            link_to_disc = link_to_disc_element['href'] if link_to_disc_element else 'No link found'

            image_element = product.find('img')
            image_url = image_element['data-src'] if image_element else 'No image found'

            result = {
                'title': title,
                'price': amount,
                'currency': currency_symbol,
                'flight_ratings': flight_ratings,
                'link_to_disc': "https://www.innovaeurope.com" + link_to_disc,
                'image_url': "https://www.innovaeurope.com" + image_url,
                'store': "innovaeurope.com"
            }

            combined = f"{result.get('title')}_{result.get('store')}"
            combined = combined.lower().replace(' ', '')
            unique_id = hashlib.sha256(combined.encode()).hexdigest()

            result["unique_id"] = unique_id

            all_products.append(result)

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
    get_data_discsport()