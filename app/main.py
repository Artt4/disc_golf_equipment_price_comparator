import json
import os
import requests
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_oauthlib.client import OAuth
from handle_credentials import get_secret
from handle_db_connections import create_conn, execute_insert, execute_select
import logging

app = Flask(__name__)

# Set up logging.
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app.secret_key = get_secret("SECRET_KEY")
app.config['GOOGLE_ID'] = get_secret("google_id")
app.config['GOOGLE_SECRET'] = get_secret("google_secret")
app.config['RECOMMENDER_URL'] = get_secret("recommender_url")

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_ID'],
    consumer_secret=app.config['GOOGLE_SECRET'],
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('product_grid'))

@app.route('/auth/callback')
def authorized():
    try:
        response = google.authorized_response()
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return redirect(url_for('home'))

    if response is None or response.get('access_token') is None:
        return 'Login failed!'

    session['google_token'] = (response['access_token'], '')
    me = google.get('userinfo').__dict__
    me = json.loads(me.get("raw_data"))

    query = """
    INSERT INTO users (id, e_mail, picture_url, product_history)
    SELECT %s, %s, %s, %s
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = %s);
    """
    insert_statements = [(me.get("id"), me.get("email"), me.get("picture"), 
                          json.dumps({'product_history': []}), me.get("id"))]
    
    connection = None
    try:
        connection = create_conn()
        execute_insert(connection, query, insert_statements)
    except Exception as e:
        logger.error(f"Insert user error: {e}")
        return 'Database error during signup!', 500
    finally:
        if connection:
            connection.close()

    session['user_email'] = me.get("email")
    session['id'] = me.get("id")

    return redirect(url_for('product_grid'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/products")
def product_grid():
    connection = None
    try:
        sql_query = """
        SELECT * FROM main_schema.product_table 
        WHERE speed IS NOT NULL AND glide IS NOT NULL AND turn IS NOT NULL AND fade IS NOT NULL;
        """
        connection = create_conn()
        products = execute_select(connection, sql_query)
        products = [process_product(product) for product in products if "karte" not in product.get("title", "").lower()]
    except Exception as e:
        logger.error(f"Product grid error: {e}")
        products = []
    finally:
        if connection:
            connection.close()

    filtered_products = filter_products(products, request.args)
    sorted_products = sort_products(filtered_products, request.args.get('sort', ''))

    page, per_page = int(request.args.get('page', 1)), 25
    paginated_products = paginate_products(sorted_products, page, per_page)

    unique_stores = set(product['store'] for product in products)

    return render_template(
        'product_grid.html',
        products=paginated_products,
        search_query=request.args.get('search', ''),
        selected_price_range=request.args.get('price_range', ''),
        selected_speed=request.args.get('speed', ''),
        selected_glide=request.args.get('glide', ''),
        selected_turn=request.args.get('turn', ''),
        selected_fade=request.args.get('fade', ''),
        selected_stores=request.args.getlist('store'),
        unique_stores=unique_stores,
        sort_option=request.args.get('sort', ''),
        page=page,
        total_pages=(len(sorted_products) + per_page - 1) // per_page,
        pages_to_display=range(page, min(page + 3, ((len(sorted_products) + per_page - 1) // per_page) + 1)),
        session=session
    )

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if "id" not in session:
        return redirect(url_for("login"))
    
    session_id = session.get('id')
    connection = None
    
    try:
        connection = create_conn()
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_json = execute_select(connection, sql_query, (session_id,))
        product_history = json.loads(user_json[0].get("product_history")).get("product_history")
        products = get_products_by_ids(connection, product_history)
        products = [process_product(product) for product in products if "karte" not in product.get("title", "").lower()]
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        products = []
    finally:
        if connection:
            connection.close()
    
    page, per_page = int(request.args.get('page', 1)), 25
    paginated_products = paginate_products(products, page, per_page)
    
    try:
        me = google.get('userinfo').__dict__
        me = json.loads(me.get("raw_data"))
        user = {'email': me.get("email"), 'picture': me.get("picture")}
    except Exception as e:
        logger.error(f"Google userinfo error: {e}")
        user = {'email': 'Unknown', 'picture': ''}

    # Get recommendation
    if os.getenv("APP_ENV") == "local":
        recommender_url = "http://localhost:8080/recommend"
    else:
        base = app.config["RECOMMENDER_URL"].rstrip("/")         
        recommender_url = base if base.endswith("/recommend") \
                            else f"{base}/recommend"            

    try:
        # give Cloud Run enough time for a cold-start
        response = requests.get(f"{recommender_url}?user_id={session_id}", timeout=20)
        response.raise_for_status()          # raise if HTTP 4xx/5xx
        recommendation = response.json()
    except requests.RequestException as e:
        logger.error(f"Recommendation error: {e}")
        recommendation = {"title": "Recommendation unavailable", "unique_id": None}
        
    return render_template(
        'profile.html', 
        products=paginated_products,
        page=page,
        total_pages=(len(products) + per_page - 1) // per_page,
        pages_to_display=range(page, min(page + 3, ((len(products) + per_page - 1) // per_page) + 1)),
        user=user,
        recommendation=recommendation,
        recommender_url=recommender_url
    )

@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    connection = None
    try:
        product_data = request.get_json()
        session_id = session.get('id')

        connection = create_conn()
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_json = execute_select(connection, sql_query, (session_id,))
        product_history = json.loads(user_json[0].get("product_history"))
        
        unique_id = product_data.get("unique_id")
        if unique_id not in product_history["product_history"]:
            product_history["product_history"].append(unique_id)

        query = "UPDATE users SET product_history = %s WHERE id = %s"
        execute_insert(connection, query, [(json.dumps(product_history), session_id)])

        return jsonify({"success": True, "message": "Added to wishlist", "unique_id": unique_id})
    except Exception as e:
        logger.error(f"Add to wishlist error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/remove-from-wishlist', methods=['POST'])
def remove_from_wishlist():
    connection = None
    try:
        product_data = request.get_json()
        session_id = session.get('id')

        connection = create_conn()
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_json = execute_select(connection, sql_query, (session_id,))
        product_history = json.loads(user_json[0].get("product_history"))
        
        unique_id = product_data.get("unique_id")
        if unique_id in product_history["product_history"]:
            product_history["product_history"].remove(unique_id)

        query = "UPDATE users SET product_history = %s WHERE id = %s"
        execute_insert(connection, query, [(json.dumps(product_history), session_id)])

        return jsonify({"success": True, "message": "Removed from wishlist", "unique_id": unique_id})
    except Exception as e:
        logger.error(f"Remove from wishlist error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/get-wishlist', methods=['GET'])
def get_wishlist():
    if "id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    session_id = session.get('id')
    connection = None
    try:
        connection = create_conn()
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_json = execute_select(connection, sql_query, (session_id,))
        product_history = json.loads(user_json[0].get("product_history")).get("product_history")
        products = get_products_by_ids(connection, product_history)
        products = [process_product(product) for product in products if "karte" not in product.get("title", "").lower()]
        return jsonify({"success": True, "products": products})
    except Exception as e:
        logger.error(f"Get wishlist error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

# Helper functions:
def process_product(product):
    if product.get('speed') is not None:
        product['speed'] = float(product['speed'])
        product['glide'] = float(product['glide'])
        product['turn'] = float(product['turn'])
        product['fade'] = float(product['fade'])
    return product

def filter_products(products, args):
    filtered = products
    query = args.get('search', '').lower()
    if query:
        filtered = [p for p in filtered if query in p['title'].lower()]
    try:
        min_price = float(args.get('price_min', 0))
    except ValueError:
        min_price = 0
    try:
        max_price = float(args.get('price_max', float('inf')))
    except ValueError:
        max_price = float('inf')
    filtered = [p for p in filtered if min_price <= float(p['price']) <= max_price]
    for attr in ['speed', 'glide', 'turn', 'fade']:
        try:
            min_val = float(args.get(f'{attr}_min', -float('inf')))
        except ValueError:
            min_val = -float('inf')
        try:
            max_val = float(args.get(f'{attr}_max', float('inf')))
        except ValueError:
            max_val = float('inf')
        filtered = [p for p in filtered if min_val <= float(p.get(attr, 0)) <= max_val]
    selected_stores = args.getlist('store')
    if selected_stores:
        filtered = [p for p in filtered if p['store'] in selected_stores]
    return filtered

def sort_products(products, sort_option):
    if sort_option == 'price_lowest':
        return sorted(products, key=lambda x: float(x['price']))
    elif sort_option == 'price_highest':
        return sorted(products, key=lambda x: float(x['price']), reverse=True)
    elif sort_option == 'title':
        return sorted(products, key=lambda x: x['title'].lower())
    elif sort_option == 'store':
        return sorted(products, key=lambda x: x['store'].lower())
    elif sort_option in ['glide_lowest', 'glide_highest', 'speed_lowest', 'speed_highest', 
                         'turn_lowest', 'turn_highest', 'fade_lowest', 'fade_highest']:
        attribute, direction = sort_option.split('_')
        return sorted(products, 
                      key=lambda x: float(x.get(attribute, 0)), 
                      reverse=(direction == 'highest'))
    return products

def paginate_products(products, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    return products[start:end]

def get_products_by_ids(connection, product_ids):
    if not product_ids:
        return []
    placeholders = ', '.join(['%s'] * len(product_ids))
    sql_query = f"""
        SELECT *
        FROM product_table
        WHERE unique_id IN ({placeholders})
    """
    return execute_select(connection, sql_query, tuple(product_ids))

if __name__ == "__main__":
    app.run(debug=False)