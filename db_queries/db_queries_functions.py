from sqlalchemy.orm import Session
from base import SessionLocal
from models.models import Book, Author
from pydantic_models import AuthorCreate, BookCreateUpdate


# ==========================
#         BOOK CRUD
# ==========================

def create_book(data: BookCreateUpdate) -> Book:
    """
    Створення нової книги.
    """
    with SessionLocal() as session:
        new_book = Book(
            title=data.title,
            publication_year=data.publication_year,
            genre=data.genre,
            description=data.description,
            author_id=data.author_id
        )
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return new_book


def get_book(book_id: int) -> Book | None:
    """
    Повертає книгу за ID.
    """
    with SessionLocal() as session:
        return session.query(Book).filter(Book.id == book_id).first()


def update_book(book_id: int, data: BookCreateUpdate) -> Book | None:
    """
    Оновлює книгу за ID.
    """
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.id == book_id).first()

        if not book:
            return None

        for key, value in data.dict().items():
            setattr(book, key, value)

        session.commit()
        session.refresh(book)
        return book


def delete_book(book_id: int) -> bool:
    """
    Видаляє книгу за ID.
    """
    with SessionLocal() as session:
        book = session.query(Book).filter(Book.id == book_id).first()

        if not book:
            return False

        session.delete(book)
        session.commit()
        return True


# ==========================
#        AUTHOR CRUD
# ==========================

def create_author(data: AuthorCreate) -> Author:
    """
    Створює нового автора.
    """
    with SessionLocal() as session:
        author = Author(**data.dict())
        session.add(author)
        session.commit()
        session.refresh(author)
        return author


def get_author(author_id: int) -> Author | None:
    with SessionLocal() as session:
        return session.query(Author).filter(Author.id == author_id).first()


def update_author(author_id: int, data: AuthorCreate) -> Author | None:
    """
    Оновлює автора за ID.
    """
    with SessionLocal() as session:
        author = session.query(Author).filter(Author.id == author_id).first()

        if not author:
            return None

        for key, value in data.dict().items():
            setattr(author, key, value)

        session.commit()
        session.refresh(author)
        return author


def delete_author(author_id: int) -> bool:
    """
    Видаляє автора за ID.
    """
    with SessionLocal() as session:
        author = session.query(Author).filter(Author.id == author_id).first()

        if not author:
            return False

        session.delete(author)
        session.commit()
        return True
