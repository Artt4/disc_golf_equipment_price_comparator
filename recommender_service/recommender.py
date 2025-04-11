import os
import pymysql
import json
from flask import Flask, jsonify, request
from collections import Counter
from handle_credentials import get_secret
from handle_db_connections import create_conn, execute_insert, execute_select

app = Flask(__name__)

def get_recommendation(user_id):
    connection = create_conn()
    cursor = connection.cursor()
    try:
        print(f"Querying user ID: {user_id}")
        
        sql_query = "SELECT product_history FROM users WHERE id = %s"
        cursor.execute(sql_query, (user_id,))
        user_data = cursor.fetchall()
        user_wishlist = json.loads(user_data[0][0])["product_history"] if user_data else []
        print(f"User wishlist: {user_wishlist}")

        if not user_wishlist:
            print("Wishlist empty, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            cursor.execute(sql_query)
            top_disc = cursor.fetchall()
            print(f"Fallback result: {top_disc}")
            return dict(zip([desc[0] for desc in cursor.description], top_disc[0])) if top_disc else {"title": "No recommendations yet", "unique_id": None}

        sql_query = "SELECT id, product_history FROM users WHERE id != %s"
        cursor.execute(sql_query, (user_id,))
        all_users = cursor.fetchall()
        all_users = [dict(zip([desc[0] for desc in cursor.description], row)) for row in all_users]
        print(f"Found {len(all_users)} other users")

        similar_users_items = []
        for user in all_users:
            wishlist = json.loads(user["product_history"])["product_history"]
            if any(item in user_wishlist for item in wishlist):
                similar_users_items.extend(wishlist)
        print(f"Similar users' items: {similar_users_items}")

        recommendations = [item for item in similar_users_items if item not in user_wishlist]
        print(f"Possible recommendations: {recommendations}")
        if not recommendations:
            print("No recommendations found, using fallback...")
            sql_query = """
            SELECT p.unique_id, p.title, p.price, p.currency, p.store, p.image_url, COUNT(*) as wishlist_count
            FROM users u, JSON_TABLE(u.product_history, '$.product_history[*]' COLUMNS (unique_id VARCHAR(255) PATH '$')) AS jt
            JOIN product_table p ON p.unique_id = jt.unique_id
            GROUP BY p.unique_id, p.title, p.price, p.currency, p.store, p.image_url
            ORDER BY wishlist_count DESC, p.price ASC
            LIMIT 1
            """
            cursor.execute(sql_query)
            top_disc = cursor.fetchall()
            return dict(zip([desc[0] for desc in cursor.description], top_disc[0])) if top_disc else {"title": "No recommendations yet", "unique_id": None}

        most_common_id = Counter(recommendations).most_common(1)[0][0]
        print(f"Most common ID: {most_common_id}")

        sql_query = "SELECT * FROM product_table WHERE unique_id = %s"
        cursor.execute(sql_query, (most_common_id,))
        recommended_product = cursor.fetchall()
        print(f"Recommended product: {recommended_product}")
        return dict(zip([desc[0] for desc in cursor.description], recommended_product[0])) if recommended_product else None
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        connection.close()

@app.route("/recommend", methods=["GET"])
def recommend():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    recommendation = get_recommendation(user_id)
    return jsonify(recommendation or {"title": "No recommendation available", "unique_id": None})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)