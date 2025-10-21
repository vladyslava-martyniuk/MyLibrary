from base import Base, SessionLocal
from models.book import Book


def create_book(title:str, author:str, publication_year:int, genre:str) -> Book:
    """
    Додає нову книгу в базу даних.
    """
    with SessionLocal() as session:
        new_book = Book(
            title=title,
            author=author,
            publication_year=publication_year,
            genre=genre
        )
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
    return new_book


def get_book(id: int) -> Book | None:
    """
    Знаходить і повертає одну книгу за її id.
    """
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.id == id).first()
        return book


def update_book(id: int, title: str = None, author: str = None, publication_year: int = None, genre: str = None) -> Book | None:
    """
    Оновлює дані існуючої книги за її id.
    """
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.id == id).first()

        if not book:
            return None

        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if publication_year is not None:
            book.publication_year = publication_year
        if genre is not None:
            book.genre = genre

        session.commit()
        session.refresh(book)
        return book


def delete_book(id: int) -> bool:
    """
    Видаляє книгу за її id. Повертає True у разі успіху, False, якщо книга не знайдена.
    """
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.id == id).first()

        if not book:
            return False

        else:
            session.delete(book)
            session.commit()
            return True
