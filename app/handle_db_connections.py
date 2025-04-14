import pymysql
import decimal
import time
from handle_credentials import get_secret

def create_conn():
    for attempt in range(3):
        try:
            connection_socket = get_secret("connection_socket")
            #connection_host = get_secret("connection_host")
            connection_user = get_secret("connection_user")
            connection_password = get_secret("connection_password")
            connection_database = get_secret("connection_database")

            return pymysql.connect(
                unix_socket=connection_socket,
                #host = connection_host,
                user=connection_user,
                password=connection_password,
                database=connection_database,
                connect_timeout=1800,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        except pymysql.err.OperationalError as e:
            if attempt == 2:
                raise
            time.sleep(1)  # Wait before retrying

def execute_insert(connection, query, statements):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.executemany(query, statements)
        connection.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"Insert error: {e}")
        connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()

def execute_select(connection, query, params=None):
    cursor = None
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Select error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()