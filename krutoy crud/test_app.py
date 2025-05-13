import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        """Настроим WebDriver для тестирования"""
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def tearDown(self):
        """Закрытие WebDriver после тестов"""
        self.driver.quit()

    def login(self, username, password):
        """Функция для выполнения логина"""
        self.driver.get("http://127.0.0.1:5000/login")
        username_input = self.driver.find_element(By.ID, "username")
        password_input = self.driver.find_element(By.ID, "password")
        login_button = self.driver.find_element(By.XPATH, "//button[text()='Login']")

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))
        )

    def test_login_admin(self):
        """Тест входа администратором"""
        self.login("admin", "admin123")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))
        )
        print("Login successful as admin")

    def test_login_user(self):
        """Тест входа пользователем"""
        self.login("user", "user123")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Welcome')]"))
        )
        print("Login successful as user")

    def test_create_order_admin(self):
        """Тест создания заказа администратором"""
        self.login("admin", "admin123")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "customer_name"))
        )
        print("Order creation form loaded")

        customer_name_input = self.driver.find_element(By.ID, "customer_name")
        book_title_input = self.driver.find_element(By.ID, "book_title")
        status_select = self.driver.find_element(By.ID, "status")
        submit_button = self.driver.find_element(By.XPATH, "//button[text()='Create Order']")

        customer_name_input.send_keys("John Doe")
        book_title_input.send_keys("Test Book")
        status_select.send_keys("Pending")
        submit_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'John Doe')]"))
        )
        new_order = self.driver.find_element(By.XPATH, "//td[contains(text(), 'John Doe')]")
        self.assertTrue(new_order.is_displayed())
        print("New order created and displayed")

    def test_view_orders_user(self):
        """Тест просмотра заказов пользователем"""
        self.login("user", "user123")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table"))
        )

        orders_table = self.driver.find_element(By.XPATH, "//table")
        self.assertTrue(orders_table.is_displayed())
        print("Orders table displayed")

    def test_logout(self):
        """Тест выхода из системы"""
        self.login("admin", "admin123")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[text()='Logout']"))
        )
        logout_button = self.driver.find_element(By.XPATH, "//a[text()='Logout']")
        logout_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Login']"))
        )
        print("Logout successful")


if __name__ == "__main__":
    unittest.main()