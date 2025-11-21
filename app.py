from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status, APIRouter
from sqlalchemy.orm import Session
from base import get_db, Base, engine

from models.models import Book, Author
from pydantic_models import (
    BookCreateUpdate,
    BookResponse,
    AuthorCreate,
    AuthorResponse
)

import shutil
import os

# Створення таблиць
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ===========================
# CRUD ФУНКЦІЇ ДЛЯ АВТОРІВ
# ===========================
def create_author(db: Session, author: AuthorCreate):
    db_author = Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_author(db: Session, author_id: int):
    return db.query(Author).filter(Author.id == author_id).first()


def update_author(db: Session, author_id: int, new_data: AuthorCreate):
    author = get_author(db, author_id)
    if not author:
        return None
    for key, value in new_data.dict().items():
        setattr(author, key, value)
    db.commit()
    db.refresh(author)
    return author


def delete_author(db: Session, author_id: int):
    author = get_author(db, author_id)
    if not author:
        return False
    db.delete(author)
    db.commit()
    return True


# ====================================
# CRUD для книг
# ====================================

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreateUpdate, db: Session = Depends(get_db)):
    # Перевірити чи існує автор
    author = db.query(Author).filter(Author.id == book_in.author_id).first()
    if not author:
        raise HTTPException(404, "Автор не знайдений")

    db_book = Book(
        title=book_in.title,
        publication_year=book_in.publication_year,
        genre=book_in.genre,
        description=book_in.description,
        author_id=book_in.author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Книгу не знайдено")
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Книга не знайдена")
    db.delete(book)
    db.commit()
    return {"message": f"Книга з ID {book_id} успішно видалена"}


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, new_data: BookCreateUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Книгу не знайдено")

    # Перевірити автора
    author = db.query(Author).filter(Author.id == new_data.author_id).first()
    if not author:
        raise HTTPException(404, "Автор не знайдений")

    for key, value in new_data.dict().items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


# ==============================
#  АВТОРИ — Ендпоінти
# ==============================

router = APIRouter(prefix="/authors", tags=["Authors"])

@router.post("/", response_model=AuthorResponse, status_code=201)
def create_author_endpoint(author: AuthorCreate, db: Session = Depends(get_db)):
    return create_author(db, author)


@router.get("/{author_id}", response_model=AuthorResponse)
def get_author_endpoint(author_id: int, db: Session = Depends(get_db)):
    author = get_author(db, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    return author


@router.put("/{author_id}", response_model=AuthorResponse)
def update_author_endpoint(author_id: int, new_data: AuthorCreate, db: Session = Depends(get_db)):
    updated = update_author(db, author_id, new_data)
    if not updated:
        raise HTTPException(404, "Author not found")
    return updated


@router.delete("/{author_id}")
def delete_author_endpoint(author_id: int, db: Session = Depends(get_db)):
    if not delete_author(db, author_id):
        raise HTTPException(404, "Author not found")
    return {"message": "Author deleted successfully"}


app.include_router(router)


# ==========================
#  ФАЙЛИ
# ==========================

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]


@app.post("/uploadfile/")
async def upload_pdf(file: UploadFile = File(...)):
    # Перевірка типу
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            400, f"Неприпустимий тип файлу. Дозволені: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    # Розрахунок розміру файлу
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            f"Файл занадто великий. Максимальний розмір: {MAX_FILE_SIZE // 1024 // 1024} MB",
        )

    # Збереження
    filepath = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "size": size}


# Запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
