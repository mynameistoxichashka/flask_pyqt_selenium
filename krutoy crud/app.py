from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flasgger import Swagger
import psycopg2

app = Flask(__name__)
app.secret_key = '123'
swagger = Swagger(app)

DB_CONFIG = {
    'dbname': 'orders',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('orders_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('orders_page'))
        elif username == "user" and password == "user123":
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('orders_page'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/orders', methods=['GET', 'POST'])
def orders_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        if 'customer_name' in request.form and 'book_title' in request.form:
            customer_name = request.form['customer_name']
            book_title = request.form['book_title']
            status = request.form.get('status', 'Pending')

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (customer_name, book_title, status) VALUES (%s, %s, %s) RETURNING id;",
                (customer_name, book_title, status)
            )
            order_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('orders_page'))

    return render_template('orders.html', orders=orders, username=session['username'], role=session['role'])

@app.route('/order/update/<int:id>', methods=['POST'])
def update_order(id):
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 401

    status = request.form['status']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE id = %s;", (status, id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('orders_page'))

@app.route('/order/delete/<int:id>', methods=['POST'])
def delete_order(id):
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = %s;", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Order deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
