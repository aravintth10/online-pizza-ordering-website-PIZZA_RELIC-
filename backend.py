from flask import Flask, request, jsonify, render_template
import pymysql
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Function to create a MySQL connection
def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="arav",  # Your MySQL password
        database="pizza_ordering",  # Your database name
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Function to create the database and tables
def create_database_and_tables():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="arav",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS pizza_ordering")
            cursor.execute("USE pizza_ordering")

            # Create the orders table
            orders_table_sql = """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                contact_number VARCHAR(15),
                total_price DECIMAL(10, 2) NOT NULL,
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(orders_table_sql)

            # Create the order_items table
            order_items_table_sql = """
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT,
                pizza_name VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
            """
            cursor.execute(order_items_table_sql)

            connection.commit()
            print("Database and tables created successfully.")

    except Exception as e:
        print(f"Error while creating database/tables: {e}")

    finally:
        connection.close()

@app.route('/', methods=['POST','GET'])
def Home():
    return render_template("index.html")



# Route to handle placing an order
@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.json  # Get data from the frontend (JSON)
    
    customer_name = data.get('customer_name')
    contact_number = data.get('contact_number')
    total_price = data.get('total_price')
    order_items = data.get('order_items')  # List of pizzas

    connection = create_connection()

    try:
        with connection.cursor() as cursor:
            # Insert into the orders table
            cursor.execute("""
                INSERT INTO orders (customer_name, contact_number, total_price) 
                VALUES (%s, %s, %s)
            """, (customer_name, contact_number, total_price))
            order_id = connection.insert_id()  # Get the last inserted order ID

            # Insert each pizza into the order_items table
            for item in order_items:
                cursor.execute("""
                    INSERT INTO order_items (order_id, pizza_name, price)
                    VALUES (%s, %s, %s)
                """, (order_id, item['name'], item['price']))
            
            connection.commit()  # Save the changes
            return jsonify({'status': 'success', 'message': 'Order placed successfully!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        connection.close()

# Create database and tables
create_database_and_tables()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)  # Run on port 5000 by default
