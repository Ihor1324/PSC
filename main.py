import hashlib
import requests
import sys
import string
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt

class PasswordChecker(QWidget):
    def check_pwned_password(self):
        password = self.input.text()

        if not password:
            self.result.setText("⚠️ Спочатку введи пароль.")
            self.strength_label.setText("")
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
                self.strength_label.setText("")
                return
        except Exception as e:
            self.result.setText(f"⚠️ Помилка мережі: {str(e)}")
            self.strength_label.setText("")
            return

        # Пошук у відповідях
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                self.result.setText(f"❌ Цей пароль злитий! Знайдено {count} раз(ів) у базі.")
                self.strength_label.setText("")
                return

        self.result.setText("✅ Цей пароль **не злитий** у публічних базах.")
        self.strength_label.setText("")
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PSC")
        self.setGeometry(170, 50, 1080, 720)

        # 🔹 Фон
        background = QPixmap("cybersecurity_background.png")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

        # 🔹 Поле для введення пароля
        self.input = QLineEdit(self)
        self.input.setEchoMode(QLineEdit.Normal)
        self.input.setPlaceholderText("Введи свій пароль")
        self.input.setGeometry(100, 100, 300, 40)
        self.input.setStyleSheet("border-radius: 10px;")

        # 🔹 Кнопка перевірки пароля за стандартами (довжина, цифри тощо)
        self.check_button = QPushButton("Перевірити стандартний пароль", self)
        self.check_button.setGeometry(100, 160, 300, 40)
        self.check_button.setStyleSheet("font-size: 18px; background-color: #2E8B57 ; color: white; border-radius: 10px;")
        self.check_button.clicked.connect(self.check_password)

        # 🔹 Кнопка перевірки пароля в списку популярних паролів
        self.check_list_button = QPushButton("Перевірити в списку популярних", self)
        self.check_list_button.setGeometry(100, 220, 300, 40)
        self.check_list_button.setStyleSheet("font-size: 18px; background-color: #C62828; color: white; border-radius: 10px;")
        self.check_list_button.clicked.connect(self.check_password_in_list)

        # 🔹 Кнопка перевірки пароля в списку злитих паролів
        self.check_pwned_button = QPushButton("Перевірити у злитих базах (HIBP)", self)
        self.check_pwned_button.setGeometry(100, 280, 300, 40)
        self.check_pwned_button.setStyleSheet("font-size: 18px; background-color: #283593; color: white; border-radius: 10px;")
        self.check_pwned_button.clicked.connect(self.check_pwned_password)

        # 🔹 Кнопка перевірки пароля на надійність
        self.crack_time_button = QPushButton("Скільки часу треба на злом?", self)
        self.crack_time_button.setGeometry(100, 340, 300, 40)
        self.crack_time_button.setStyleSheet("font-size: 18px; background-color: #EF6C00; color: white; border-radius: 10px;")
        self.crack_time_button.clicked.connect(self.estimate_crack_time)

        # Кнопка, яка запускає генерацію (етап 1)
        self.start_generate_button = QPushButton("Згенерувати надійний пароль", self)
        self.start_generate_button.setGeometry(100, 400, 300, 40)
        self.start_generate_button.setStyleSheet("font-size: 18px; background-color: #6A1B9A; color: white; border-radius: 10px;")
        self.start_generate_button.clicked.connect(self.show_length_input)

        # Поле для введення довжини пароля (приховано спочатку)
        self.length_input = QLineEdit(self)
        self.length_input.setPlaceholderText("Введи довжину пароля")
        self.length_input.setGeometry(100, 400, 300, 40)
        self.length_input.setStyleSheet("font-size: 12px; border-radius: 10px;")
        self.length_input.hide()

        # Кнопка генерації (прихована спочатку)
        self.generate_button = QPushButton("Згенерувати", self)
        self.generate_button.setGeometry(100, 460, 300, 40)
        self.generate_button.setStyleSheet("font-size: 18px; background-color: #6A1B9A; color: white; border-radius: 10px;")
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.hide()

        # 🔹 Результат
        self.result = QLabel(self)
        self.result.setGeometry(100, 500, 600, 200)
        self.result.setStyleSheet("color: white; font-size: 16px;")
        self.result.setWordWrap(True)

        # 🔹 Оцінка сили пароля
        self.strength_label = QLabel(self)
        self.strength_label.setGeometry(100, 650, 700, 50)
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
            self.strength_label.setText("")
        else:
            self.result.setText("✅ Пароль не знайдено в списку небезпечних.")
            self.strength_label.setText("")

    def estimate_crack_time(self):
        password = self.input.text()
        if not password:
            self.result.setText("⚠️ Спочатку введи пароль.")
            self.strength_label.setText("")
            return

        has_digit = any(char.isdigit() for char in password)
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_special = any(char in string.punctuation for char in password)

        charset_size = 0
        if has_digit:
            charset_size += 10
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_special:
            charset_size += 33  # приблизно

        if charset_size == 0:
            self.result.setText("⚠️ Символи не виявлені.")
            return

        combinations = charset_size ** len(password)
        guess_rate_user = 1_000_000      # 1 млн/сек
        guess_rate_super = 1_000_000_000 # 1 млрд/сек

        seconds_user = combinations / guess_rate_user
        seconds_super = combinations / guess_rate_super

        def format_time(seconds):
            if seconds < 60:
                return f"{seconds:.2f} секунд"
            elif seconds < 3600:
                return f"{seconds/60:.2f} хвилин"
            elif seconds < 86400:
                return f"{seconds/3600:.2f} годин"
            elif seconds < 31536000:
                return f"{seconds/86400:.2f} днів"
            else:
                return f"{seconds/31536000:.2f} років"

        message = (
            "⏱️ Оцінка часу для перебору пароля:\n\n"
            f"🖥️ На звичайному ПК: {format_time(seconds_user)}\n"
            f"💻 На суперкомп’ютері: {format_time(seconds_super)}"
        )

        self.result.setText(message)
        self.strength_label.setText("")


    def show_length_input(self):
        self.start_generate_button.hide()     # ховаємо першу кнопку
        self.length_input.show()              # показуємо поле довжини
        self.generate_button.show()   
        self.result.setText("")
        self.strength_label.setText("")        # показуємо кнопку "Згенерувати"

    def generate_password(self):
        try:
            length = int(self.length_input.text())
            if length < 0 or length > 100:
                self.result.setText("⚠️ Довжина має бути від 1 до 100.")
                self.strength_label.setText("")
                return
        except ValueError:
            self.result.setText("⚠️ Введи ціле число для довжини.")
            self.strength_label.setText("")
            return

        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))

        self.input.setText(password)
        self.result.setText(f"🔐 Згенеровано пароль з {length} символів.")
        self.strength_label.setText("")
        self.start_generate_button.show()     # ховаємо першу кнопку
        self.length_input.hide()              # показуємо поле довжини
        self.generate_button.hide()           # показуємо кнопку "Згенерувати"
        self.result.setText("")

# 🔹 Запуск програми
app = QApplication(sys.argv)
window = PasswordChecker()
window.show()
sys.exit(app.exec_())
