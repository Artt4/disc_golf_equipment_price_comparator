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

def get_data_par3():

    url_placeholder = 1

    while True:

        all_products = []

        print("getting par3 page")
        page_url = f"https://www.par3.lv/collections/disku-golfa-diski?page={url_placeholder}"


        
        response = requests.get(page_url)

        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        ############################################################################################

        parent_div = soup.find('product-list', class_="product-list")

        if not parent_div:
            break

        products = parent_div.find_all('product-card', recursive=False)

        for product in products:

            title = product.find('span', class_="product-card__title").get_text(strip=True)

            if product.find('sale-price') is not None:
                price_element = product.find('sale-price')
                price_element = price_element.contents[-1].strip()

            numeric_value = ''.join([char for char in price_element if char.isdigit() or char == ',' or char == '.'])
            currency_symbol = ''.join([char for char in price_element if not char.isdigit() and char != ',' and char != '.'])
            amount = float(numeric_value.replace(",", "."))

            flight_ratings = {}
            spec_card = product.find('div', class_='specs_card')

            if spec_card:
                text_content = spec_card.get_text(strip=True)
                flight_rating_element = [element.strip() for element in text_content.split('|')]
                flight_ratings['Speed'] = flight_rating_element[0]
                flight_ratings['Glide'] = flight_rating_element[1]
                flight_ratings['Turn'] = flight_rating_element[2]
                flight_ratings['Fade'] = flight_rating_element[3]
            else:
                flight_ratings['Speed'] = None
                flight_ratings['Glide'] = None
                flight_ratings['Turn'] = None
                flight_ratings['Fade'] = None

            if flight_ratings.get('Speed') == '':
                flight_ratings['Speed'] = None
            if flight_ratings.get('Glide') == '':
                flight_ratings['Glide'] = None
            if flight_ratings.get('Turn') == '':
                flight_ratings['Turn'] = None
            if flight_ratings.get('Fade') == '':
                flight_ratings['Fade'] = None

            link_to_disc_element = product.find('a')
            link_to_disc = "https://par3.lv" + link_to_disc_element['href'] if link_to_disc_element else 'No link found'

            images = product.find('div', class_="product-card__figure")
            image_url = "https://" + images.find_all("img")[0]["src"].replace("//", "")

            result = {
                'title': title,
                'price': amount,
                'currency': currency_symbol,
                'flight_ratings': flight_ratings,
                'link_to_disc': link_to_disc,
                'image_url': image_url,
                'store': "par3.lv"
            }

            combined = f"{result.get('title')}_{result.get('store')}"
            combined = combined.lower().replace(' ', '')
            unique_id = hashlib.sha256(combined.encode()).hexdigest()

            result["unique_id"] = unique_id

            all_products.append(result)

        url_placeholder = url_placeholder + 1

        pagination_span = soup.find('span', class_='pagination__current')
        if pagination_span:
            try:
                current, max_page = pagination_span.get_text(strip=True).split('/')
                current_page = int(current.strip())
                max_page = int(max_page.strip())
                if url_placeholder > max_page:
                    print(f"Reached end: page {url_placeholder} > {max_page}")
                    break
            except Exception as e:
                print(f"⚠️ Could not parse pagination: {e}")
                break
        else:
            print("⚠️ Pagination element not found, assuming last page")
            break

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
    get_data_par3()