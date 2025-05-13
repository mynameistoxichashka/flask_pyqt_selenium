import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, \
    QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt

DB_CONFIG = {
    'dbname': 'orders',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '5432'
}


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Form")
        self.setGeometry(100, 100, 300, 200)

        self.layout = QVBoxLayout()

        self.username_label = QLabel('Username:')
        self.layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:')
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.handle_login)
        self.layout.addWidget(self.login_button)

        self.result_label = QLabel('')
        self.layout.addWidget(self.result_label)

        self.setLayout(self.layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "admin123":
            self.result_label.setText("Welcome Admin!")
            self.open_admin_window()
        elif username == "user" and password == "user123":
            self.result_label.setText("Welcome User!")
            self.open_user_window()
        else:
            self.result_label.setText("Invalid username or password!")

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()

    def open_user_window(self):
        self.user_window = UserWindow()
        self.user_window.show()
        self.close()


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Window")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()

        self.order_list = QListWidget()
        self.layout.addWidget(self.order_list)

        self.add_order_button = QPushButton('Add Order')
        self.add_order_button.clicked.connect(self.add_order)
        self.layout.addWidget(self.add_order_button)

        self.delete_order_button = QPushButton('Delete Order')
        self.delete_order_button.clicked.connect(self.delete_order)
        self.layout.addWidget(self.delete_order_button)

        self.update_order_button = QPushButton('Update Order Status')
        self.update_order_button.clicked.connect(self.update_order)
        self.layout.addWidget(self.update_order_button)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pending", "Shipped", "Delivered", "Cancelled"])
        self.layout.addWidget(self.status_combo)

        self.load_orders()

        self.setLayout(self.layout)

    def load_orders(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            self.order_list.clear()

            for order in orders:
                self.order_list.addItem(f"Order ID: {order[0]}, {order[1]} - {order[3]}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading orders: {e}")

    def add_order(self):
        customer_name = "New Customer"
        book_title = "New Book"
        status = "Pending"

        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (customer_name, book_title, status) VALUES (%s, %s, %s) RETURNING id;",
                (customer_name, book_title, status)
            )
            conn.commit()
            order_id = cursor.fetchone()[0]
            print(f"Order added with ID: {order_id}")
            cursor.close()
            conn.close()

            self.load_orders()

        except Exception as e:
            print(f"Error adding order: {e}")

    def delete_order(self):
        selected_item = self.order_list.currentItem()
        if selected_item:
            order_id = int(selected_item.text().split()[2][:-1])  # Извлекаем ID из строки
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM orders WHERE id = %s;", (order_id,))
                conn.commit()
                cursor.close()
                conn.close()

                print(f"Order with ID {order_id} deleted.")
                self.load_orders()

            except Exception as e:
                print(f"Error deleting order: {e}")

    def update_order(self):
        selected_item = self.order_list.currentItem()
        if selected_item:
            order_id = int(selected_item.text().split()[2][:-1])
            status = self.status_combo.currentText()

            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET status = %s WHERE id = %s;", (status, order_id))
                conn.commit()
                cursor.close()
                conn.close()

                print(f"Order with ID {order_id} updated to {status}.")
                self.load_orders()

            except Exception as e:
                print(f"Error updating order: {e}")


class UserWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Window")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()

        # Список заказов
        self.order_list = QListWidget()
        self.layout.addWidget(self.order_list)

        self.load_orders()

        self.setLayout(self.layout)

    def load_orders(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
            orders = cursor.fetchall()
            self.order_list.clear()

            for order in orders:
                self.order_list.addItem(f"Order ID: {order[0]}, {order[1]} - {order[3]}")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error loading orders: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())