import os
import pymysql
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import Counter
from handle_credentials import get_secret
from handle_db_connections import create_conn, execute_insert, execute_select
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for webapp requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_recommendation(user_id):
    connection = None
    try:
        connection = create_conn()
        logger.debug(f"Querying user ID: {user_id}")
        
        # Get user's wishlist
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_data = execute_select(connection, sql_query, (user_id,))
        user_wishlist = json.loads(user_data[0].get("product_history"))["product_history"] if user_data else []
        logger.debug(f"User wishlist: {user_wishlist}")

        if not user_wishlist:
            logger.info("Wishlist empty, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, p.speed, p.glide, p.turn, p.fade, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, p.speed, p.glide, p.turn, p.fade
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            top_disc = execute_select(connection, sql_query)
            logger.debug(f"Fallback result: {top_disc}")
            return dict(top_disc[0]) if top_disc else {"title": "No recommendations yet", "unique_id": None}

        # Get other users' wishlists
        sql_query = "SELECT id, product_history FROM users WHERE id != %s"
        all_users = execute_select(connection, sql_query, (user_id,))
        logger.debug(f"Found {len(all_users)} other users")

        similar_users_items = []
        for user in all_users:
            wishlist = json.loads(user["product_history"])["product_history"]
            if any(item in user_wishlist for item in wishlist):
                similar_users_items.extend(wishlist)
        logger.debug(f"Similar users' items: {similar_users_items}")

        recommendations = [item for item in similar_users_items if item not in user_wishlist]
        logger.debug(f"Possible recommendations: {recommendations}")
        if not recommendations:
            logger.info("No recommendations found, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, p.speed, p.glide, p.turn, p.fade, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, p.speed, p.glide, p.turn, p.fade
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            top_disc = execute_select(connection, sql_query)
            logger.debug(f"Fallback result: {top_disc}")
            return dict(top_disc[0]) if top_disc else {"title": "No recommendations yet", "unique_id": None}

        most_common_id = Counter(recommendations).most_common(1)[0][0]
        logger.debug(f"Most common ID: {most_common_id}")

        sql_query = "SELECT unique_id, title, price, currency, store, image_url, link_to_disc, speed, glide, turn, fade FROM product_table WHERE unique_id = %s"
        recommended_product = execute_select(connection, sql_query, (most_common_id,))
        logger.debug(f"Recommended product: {recommended_product}")
        return dict(recommended_product[0]) if recommended_product else {"title": "No recommendation available", "unique_id": None}
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return {"title": "No recommendation available", "unique_id": None}
    finally:
        if connection:
            connection.close()

@app.route("/recommend", methods=["GET"])
def recommend():
    user_id = request.args.get("user_id")
    logger.debug(f"Received request for user_id: {user_id}")
    if not user_id:
        logger.warning("Missing user_id")
        return jsonify({"error": "Missing user_id"}), 400
    try:
        recommendation = get_recommendation(user_id)
        logger.debug(f"Returning recommendation: {recommendation}")
        return jsonify(recommendation)
    except Exception as e:
        logger.error(f"Recommend endpoint error: {e}")
        return jsonify({"title": "No recommendation available", "unique_id": None}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)