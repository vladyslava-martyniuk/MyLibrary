import sqlite3

# Підключення до бази
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# =========================
#  ДОДАЄМО КОРИСТУВАЧА
# =========================
cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))
admin_id = cursor.lastrowid

# =========================
#  ДОДАЄМО АВТОРІВ
# =========================
authors = [
    ("Ліна Костенко", "Україна"),
    ("Іван Франко", "Україна"),
    ("Леся Українка", "Україна"),
]

author_ids = {}
for full_name, country in authors:
    cursor.execute(
        "INSERT INTO authors (full_name, country) VALUES (?, ?)", (full_name, country)
    )
    author_ids[full_name] = cursor.lastrowid

# =========================
#  ДОДАЄМО КНИГИ
# =========================
books = [
    ("Маруся Чурай", 1979, "Роман", "Історичний роман про українську героїню", "Ліна Костенко"),
    ("Захар Беркут", 1883, "Історичний", "Розповідь про боротьбу карпатських людей", "Іван Франко"),
    ("Лісова пісня", 1911, "Драма", "Міфологічна драма про кохання та природу", "Леся Українка"),
    ("Захар Беркут", 1883, "Історичний", "Розповідь про боротьбу карпатських людей", "Іван Франко"),
]

for title, year, genre, description, author_name in books:
    author_id = author_ids[author_name]
    cursor.execute(
        "INSERT INTO books (title, publication_year, genre, description, author_id, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (title, year, genre, description, author_id, admin_id)
    )

conn.commit()
conn.close()

print("Дані успішно додані до бази library.db!")
