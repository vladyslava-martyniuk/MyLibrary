import sqlite3

# Підключення до бази
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

# Список авторів
authors = [
    ("Ліна Костенко", "Україна"),
    ("Іван Франко", "Україна"),
    ("Леся Українка", "Україна"),
    ("Василь Стефаник", "Україна"),
]

# Додаємо авторів
author_ids = {}
for full_name, country in authors:
    cursor.execute("INSERT INTO authors (full_name, country) VALUES (?, ?)", (full_name, country))
    author_ids[full_name] = cursor.lastrowid

# Список книг (title, year, genre, description, author_full_name)
books = [
    ("Маруся Чурай", 1979, "Роман", "Історичний роман про українську героїню", "Ліна Костенко"),
    ("Захар Беркут", 1883, "Історичний", "Розповідь про боротьбу карпатських людей", "Іван Франко"),
    ("Лісова пісня", 1911, "Драма", "Міфологічна драма про кохання та природу", "Леся Українка"),
    ("Захар Беркут", 1883, "Історичний", "Розповідь про боротьбу карпатських людей", "Василь Стефаник"),
]

# Додавання книги
for title, year, genre, description, author_name in books:
    author_id = author_ids[author_name]
    cursor.execute(
        "INSERT INTO books (title, publication_year, genre, description, author_id) VALUES (?, ?, ?, ?, ?)",
        (title, year, genre, description, author_id)
    )

conn.commit()
conn.close()

print("Дані успішно додані до бази library.db!")
