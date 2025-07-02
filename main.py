import hashlib
import requests
import sys
import string
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt

class PasswordChecker(QWidget):
    def check_pwned_password(self):
        password = self.input.text()

        if not password:
            self.result.setText("⚠️ Спочатку введи пароль.")
            return

        # Хешування пароля (SHA1)
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        # Запит до API HaveIBeenPwned
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.result.setText("⚠️ Помилка при зверненні до HIBP API.")
                return
        except Exception as e:
            self.result.setText(f"⚠️ Помилка мережі: {str(e)}")
            return

        # Пошук у відповідях
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                self.result.setText(f"❌ Цей пароль злитий! Знайдено {count} раз(ів) у базі.")
                return

        self.result.setText("✅ Цей пароль **не злитий** у публічних базах.")
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Перевірка пароля")
        self.setGeometry(170, 50, 1080, 720)

        # 🔹 Фон
        background = QPixmap("cybersecurity_background.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # 🔹 Поле для введення пароля
        self.input = QLineEdit(self)
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setPlaceholderText("Введи свій пароль")
        self.input.setGeometry(100, 100, 300, 40)

        # 🔹 Кнопка перевірки пароля за стандартами (довжина, цифри тощо)
        self.check_button = QPushButton("Перевірити стандартний пароль", self)
        self.check_button.setGeometry(100, 160, 300, 40)
        self.check_button.setStyleSheet("font-size: 18px; background-color: green; color: white;")
        self.check_button.clicked.connect(self.check_password)

        # 🔹 Кнопка перевірки пароля в списку популярних паролів
        self.check_list_button = QPushButton("Перевірити в списку популярних", self)
        self.check_list_button.setGeometry(100, 220, 300, 40)
        self.check_list_button.setStyleSheet("font-size: 18px; background-color: red; color: white;")
        self.check_list_button.clicked.connect(self.check_password_in_list)

        self.check_pwned_button = QPushButton("Перевірити у злитих базах (HIBP)", self)
        self.check_pwned_button.setGeometry(100, 280, 300, 40)
        self.check_pwned_button.setStyleSheet("font-size: 18px; background-color: navy; color: white;")
        self.check_pwned_button.clicked.connect(self.check_pwned_password)


        # 🔹 Результат
        self.result = QLabel(self)
        self.result.setGeometry(100, 340, 600, 200)
        self.result.setStyleSheet("color: white; font-size: 16px;")
        self.result.setWordWrap(True)

        # 🔹 Оцінка сили пароля
        self.strength_label = QLabel(self)
        self.strength_label.setGeometry(100, 500, 600, 50)
        self.strength_label.setStyleSheet("font-size: 20px; color: yellow;")
        self.strength_label.setWordWrap(True)

        # 🔹 Список популярних паролів
        self.popular_passwords = ["123456", "password", "admin", "qwerty", "letmein"]

    # 🔹 Функція для перевірки пароля за стандартами (довжина, цифри, великі/малі літери, спецсимволи)
    def check_password(self):
        password = self.input.text()
        messages = []

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in string.punctuation for char in password)

        if len(password) < 8:
            messages.append("⚠️ Пароль надто короткий!")
        else:
            messages.append("✅ Довжина пароля достатня.")

        if has_digit:
            messages.append("✅ Є цифри.")
        else:
            messages.append("❌ Немає цифр.")

        if has_upper:
            messages.append("✅ Є великі літери.")
        else:
            messages.append("❌ Немає великих літер.")

        if has_lower:
            messages.append("✅ Є малі літери.")
        else:
            messages.append("❌ Немає малих літер.")

        if has_special:
            messages.append("✅ Є спецсимволи.")
        else:
            messages.append("❌ Немає спецсимволів.")

        # Виведення результатів перевірки
        self.result.setText("\n".join(messages))

        # 🔹 Оцінка сили пароля
        strength = 0
        if len(password) >= 8:
            strength += 1
        if has_digit:
            strength += 1
        if has_upper:
            strength += 1
        if has_lower:
            strength += 1
        if has_special:
            strength += 1

        # 🔹 Підсумкова оцінка
        if strength == 5:
            final_msg = "🔐 Пароль надійний ✅"
        elif strength >= 3:
            final_msg = "🛡️ Пароль середній ⚠️"
        else:
            final_msg = "🚫 Пароль слабкий ❌"

        self.strength_label.setText(final_msg)

    # 🔹 Функція для перевірки пароля в списку популярних паролів
    def check_password_in_list(self):
        password = self.input.text()
        if password in self.popular_passwords:
            self.result.setText("⚠️ Пароль знайдено в списку небезпечних! Спробуйте інший.")
        else:
            self.result.setText("✅ Пароль не знайдено в списку небезпечних.")

# 🔹 Запуск програми
app = QApplication(sys.argv)
window = PasswordChecker()
window.show()
sys.exit(app.exec_())
