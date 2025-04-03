import sys
import os
import requests
import time
import hashlib

from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET

current_directory = os.path.dirname(os.path.realpath(__file__))
target_directory_name = 'disc_golf_equipment_price_comparator'
while current_directory:
    sys.path.append(current_directory)
    if os.path.basename(current_directory) == target_directory_name:
        break
    current_directory = os.path.dirname(current_directory)

from handle_db_connections import create_conn

def get_all_pages_latitude64():

    all_urls = []
    
    sitemap_url = "https://latitude64.com/sitemap_products_1.xml?from=2008270274629&to=9570245083483"

    response = requests.get(sitemap_url)

    if response.status_code == 200:

        sitemap_xml = ET.fromstring(response.content)
        
        urls = [
            url_elem.text for url_elem in sitemap_xml.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        ]
        
        for url in urls:
            if url != "https://latitude64.com/":
                all_urls.append(url)

    else:
        print(f"Failed to retrieve sitemap: {response.status_code}")

    return all_urls

def get_data_latitude64(all_urls):

    connection = create_conn()

    for url in all_urls:

        print("getting latitude64 page")

        page_url = url
        html_content = requests.get(page_url).text
        time.sleep(1)
        soup = BeautifulSoup(html_content, 'html.parser')

        ############################################################################################

        title_element = soup.find('h1', class_='product-info__title h2')
        title = title_element.get_text(strip=True)  

        price_element = soup.find('sale-price')
        for sr_span in price_element.find_all('span', class_='sr-only'):
            sr_span.decompose()
        price = price_element.get_text(strip=True)
        price = price.replace(' ', '')
        numeric_value = ''.join(char for char in price if char.isdigit() or char in ',.')
        currency_symbol = ''.join(char for char in price if not char.isdigit() and char not in ',.').replace("$", "€").replace("USD", "")
        
        flight_ratings = {"Speed": None, "Glide": None, "Turn": None, "Fade": None}
        chart_rows = soup.find_all("div", class_="feature-chart__table-row")

        for row in chart_rows:
            heading = row.find("div", class_="feature-chart__heading")
            value_div = row.find("div", class_="feature-chart__value")
            if heading and value_div:
                label = heading.get_text(strip=True)
                value = value_div.get_text(strip=True)
                if label in flight_ratings:
                    flight_ratings[label] = value.replace(",", ".")

        image_element = soup.find('img', class_='rounded')
        image_url = image_element['src']

        ############################################################################################

        product = {
            'title': title,
            'price': numeric_value,
            'currency': currency_symbol,
            'flight_ratings': flight_ratings,
            'link_to_disc': page_url,
            'image_url': image_url,
            'store': "latitude64.com"
        }

        combined = f"{product.get('title')}_{product.get('store')}"
        combined = combined.lower().replace(' ', '')
        unique_id = hashlib.sha256(combined.encode()).hexdigest()
        product["unique_id"] = unique_id


        ############################################################################################
        if any(v is not None for v in flight_ratings.values()):
            # proceed with the insert
            with connection.cursor() as cursor:
                        with connection.cursor() as cursor:

                            sql = """
                            INSERT INTO product_table (unique_id, title, price, currency, speed, glide, turn, fade, link_to_disc, image_url, store)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
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
                            ]

                            cursor.executemany(sql, data)
                            connection.commit()

        else:
            print(f"Skipping non-disc product: {title}")

    connection.close()

if __name__ == "__main__":
    urls = get_all_pages_latitude64()  # Fetch URLs first
    get_data_latitude64(urls)  # Pass to scraper