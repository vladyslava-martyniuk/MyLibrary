from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from base import get_db, Base, engine

from security import ACCESS_TOKEN_EXPIRE_MINUTES, Token, get_current_user, create_access_token
from passlib.context import CryptContext
from security import get_current_user
from datetime import timedelta

from dotenv import load_dotenv

from models.models import Book, Author, User
from pydantic_models import (
    BookCreateUpdate,
    BookResponse,
    AuthorCreate,
    AuthorResponse,
    UserCreate,
    UserResponse
)

import shutil
import os

from middleware.headers import SecurityHeadersMiddleware
# =========================
#  КОНФІГУРАЦІЯ .env
# =========================
# load_dotenv()

# SECRET_KEY = os.getenv("JWT_SECRET_KEY")
# ALGORITHM = [os.getenv("JWT_ALGORITHM", "HS512")]
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
#
# if not SECRET_KEY:
#     raise ValueError("JWT_SECRET_KEY не встановлений")

from security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# =========================
#  ХЕШУВАННЯ
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


# =========================
#  Створення таблиць
# =========================
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SecurityHeadersMiddleware)

# =========================
#  CRUD ФУНКЦІЇ ДЛЯ АВТОРІВ
# =========================
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


# =========================
#  CRUD ФУНКЦІЇ ДЛЯ КОРИСТУВАЧІВ
# =========================
def create_user(db: Session, user: UserCreate):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, new_data: UserCreate):
    user = get_user(db, user_id)
    if not user:
        return None
    for key, value in new_data.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


# =========================
#  CRUD ФУНКЦІЇ ДЛЯ КНИГ
# =========================
@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreateUpdate, db: Session = Depends(get_db)):
    # Перевірка автора
    author = db.query(Author).filter(Author.id == book_in.author_id).first()
    if not author:
        raise HTTPException(404, "Автор не знайдений")

    # Перевірка користувача
    user = db.query(User).filter(User.id == book_in.user_id).first()
    if not user:
        raise HTTPException(404, "Користувач не знайдений")

    db_book = Book(
        title=book_in.title,
        publication_year=book_in.publication_year,
        genre=book_in.genre,
        description=book_in.description,
        author_id=book_in.author_id,
        user_id=book_in.user_id
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


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, new_data: BookCreateUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Книгу не знайдено")

    # Перевірка автора та користувача
    author = db.query(Author).filter(Author.id == new_data.author_id).first()
    if not author:
        raise HTTPException(404, "Автор не знайдений")

    user = db.query(User).filter(User.id == new_data.user_id).first()
    if not user:
        raise HTTPException(404, "Користувач не знайдений")

    for key, value in new_data.dict().items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(404, "Книга не знайдена")
    db.delete(book)
    db.commit()
    return {"message": f"Книга з ID {book_id} успішно видалена"}


# =========================
#  ROUTER ДЛЯ АВТОРІВ
# =========================
author_router = APIRouter(prefix="/authors", tags=["Authors"])

@author_router.post("/", response_model=AuthorResponse, status_code=201)
def create_author_endpoint(author: AuthorCreate, db: Session = Depends(get_db)):
    return create_author(db, author)


@author_router.get("/{author_id}", response_model=AuthorResponse)
def get_author_endpoint(author_id: int, db: Session = Depends(get_db)):
    author = get_author(db, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    return author


@author_router.put("/{author_id}", response_model=AuthorResponse)
def update_author_endpoint(author_id: int, new_data: AuthorCreate, db: Session = Depends(get_db)):
    updated = update_author(db, author_id, new_data)
    if not updated:
        raise HTTPException(404, "Author not found")
    return updated


@author_router.delete("/{author_id}")
def delete_author_endpoint(author_id: int, db: Session = Depends(get_db)):
    if not delete_author(db, author_id):
        raise HTTPException(404, "Author not found")
    return {"message": "Author deleted successfully"}


# =========================
#  ROUTER ДЛЯ КОРИСТУВАЧІВ
# =========================
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserResponse, status_code=201)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    # В схеме UserCreate должно быть поле 'password'
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Пользователь с таким именем уже существует")

    return create_user(db, user)


@user_router.get("/me/", response_model=UserResponse)  # НОВЫЙ ЭНДПОИНТ
def read_users_me(current_user: User = Depends(get_current_user)):
    """Возвращает данные текущего аутентифицированного пользователя."""
    return current_user


@user_router.post("/", response_model=UserResponse, status_code=201)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@user_router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@user_router.put("/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, new_data: UserCreate, db: Session = Depends(get_db)):
    updated = update_user(db, user_id, new_data)
    if not updated:
        raise HTTPException(404, "User not found")
    return updated


@user_router.delete("/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    if not delete_user(db, user_id):
        raise HTTPException(404, "User not found")
    return {"message": "User deleted successfully"}


# =========================
#  ROUTER ДЛЯ АУТЕНТИФІКАЦІЇ
# =========================
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},  # 'sub' - это Subject (тема), обычно ID или username
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# =========================
#  FILE UPLOAD
# =========================
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]


@app.post("/uploadfile/")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            400, f"Неприпустимий тип файлу. Дозволені: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            413,
            f"Файл занадто великий. Максимальний розмір: {MAX_FILE_SIZE // 1024 // 1024} MB",
        )

    os.makedirs("uploads", exist_ok=True)
    filepath = f"uploads/{file.filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "size": size}


@app.get("/uploads/{filename}")
def get_uploaded_file(filename: str):
    path = f"uploads/{filename}"
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    return {"filename": filename, "path": path}


# =========================
#  INCLUDE ROUTERS
# =========================
app.include_router(auth_router)
app.include_router(author_router)
app.include_router(user_router)


# =========================
#  RUN APP
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
