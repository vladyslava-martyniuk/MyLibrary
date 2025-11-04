from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from base import get_db, Base, engine
from models.book import Book
from schemas import BookCreateUpdate, BookResponse

app = FastAPI()

@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreateUpdate, db: Session = Depends(get_db)):
    db_book = Book(
        title=book_in.title,
        author=book_in.author,
        publication_year=book_in.publication_year,
        genre=book_in.genre,
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
