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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_recommendation(user_id):
    connection = None
    try:
        connection = create_conn()
        if not connection:
            logger.error("Failed to create database connection")
            return {"title": "No recommendation available", "unique_id": None}
        logger.debug(f"Querying user ID: {user_id}")
        
        # Get user's wishlist
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        user_data = execute_select(connection, sql_query, (user_id,))
        logger.debug(f"Raw user_data: {user_data}")
        user_wishlist = json.loads(user_data[0].get("product_history"))["product_history"] if user_data else []
        logger.debug(f"User wishlist: {user_wishlist}")

        # Ensure user_wishlist is a list of strings (unique_ids)
        if not isinstance(user_wishlist, list):
            logger.warning(f"User wishlist is not a list: {user_wishlist}")
            user_wishlist = []
        user_wishlist_set = set(user_wishlist)  # For faster lookups
        logger.debug(f"User wishlist set: {user_wishlist_set}")

        if not user_wishlist:
            logger.info("Wishlist empty, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, 
                   p.speed, p.glide, p.turn, p.fade, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            WHERE p.unique_id NOT IN (%s)
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, 
                     p.speed, p.glide, p.turn, p.fade
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            placeholders = ','.join(['%s'] * len(user_wishlist)) or "'__DUMMY__'"  # Avoid empty IN clause
            top_disc = execute_select(connection, sql_query, tuple(user_wishlist) if user_wishlist else ('__DUMMY__',))
            logger.debug(f"Fallback query result (wishlist empty): {top_disc}")
            if top_disc:
                result = dict(top_disc[0])
                logger.debug(f"Fallback recommendation: {result}")
                return result
            logger.warning("No fallback recommendation found")
            return {"title": "No recommendations yet", "unique_id": None}

        # Get other users' wishlists
        sql_query = "SELECT id, product_history FROM users WHERE id != %s"
        all_users = execute_select(connection, sql_query, (user_id,))
        logger.debug(f"Other users count: {len(all_users)}, data: {all_users}")

        similar_users_items = []
        for user in all_users:
            wishlist = json.loads(user["product_history"])["product_history"]
            if not isinstance(wishlist, list):
                logger.warning(f"Invalid wishlist for user {user['id']}: {wishlist}")
                continue
            if any(item in user_wishlist_set for item in wishlist):
                similar_users_items.extend(wishlist)
        logger.debug(f"Similar users' items: {similar_users_items}")

        # Filter out items already in user's wishlist
        recommendations = [item for item in similar_users_items if item not in user_wishlist_set]
        logger.debug(f"Possible recommendations after filtering: {recommendations}")

        if not recommendations:
            logger.info("No recommendations found, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, 
                   p.speed, p.glide, p.turn, p.fade, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            WHERE p.unique_id NOT IN (%s)
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, p.link_to_disc, 
                     p.speed, p.glide, p.turn, p.fade
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            placeholders = ','.join(['%s'] * len(user_wishlist)) or "'__DUMMY__'"
            top_disc = execute_select(connection, sql_query, tuple(user_wishlist))
            logger.debug(f"Fallback query result: {top_disc}")
            if top_disc:
                result = dict(top_disc[0])
                # Double-check fallback result isn't in wishlist
                if result.get("unique_id") in user_wishlist_set:
                    logger.warning(f"Fallback recommended an item already in wishlist: {result}")
                    return {"title": "No new recommendations", "unique_id": None}
                logger.debug(f"Fallback recommendation: {result}")
                return result
            logger.warning("No fallback recommendation found")
            return {"title": "No new recommendations", "unique_id": None}

        most_common_id = Counter(recommendations).most_common(1)[0][0]
        logger.debug(f"Most common ID: {most_common_id}")

        # Double-check the recommended item isn't in the wishlist
        if most_common_id in user_wishlist_set:
            logger.warning(f"Most common ID {most_common_id} is already in wishlist")
            return {"title": "No new recommendations", "unique_id": None}

        sql_query = """
        SELECT unique_id, title, price, currency, store, image_url, link_to_disc, 
               speed, glide, turn, fade 
        FROM product_table 
        WHERE unique_id = %s
        """
        recommended_product = execute_select(connection, sql_query, (most_common_id,))
        logger.debug(f"Recommended product query result: {recommended_product}")
        if recommended_product:
            result = dict(recommended_product[0])
            logger.debug(f"Final recommendation: {result}")
            return result
        logger.warning("No product found for most common ID")
        return {"title": "No new recommendations", "unique_id": None}
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return {"title": "No recommendation available", "unique_id": None}
    finally:
        if connection:
            try:
                connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

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
        logger.error(f"Recommend endpoint error: {e}", exc_info=True)
        return jsonify({"title": "No recommendation available", "unique_id": None}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)