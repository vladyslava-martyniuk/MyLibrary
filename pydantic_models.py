from pydantic import BaseModel


# ==========================
#    АВТОРИ (Pydantic)
# ==========================
class AuthorCreate(BaseModel):
    full_name: str
    country: str | None = None


class AuthorResponse(BaseModel):
    id: int
    full_name: str
    country: str | None = None

    class Config:
        orm_mode = True


# ==========================
#    КНИГИ (Pydantic)
# ==========================
class BookCreateUpdate(BaseModel):
    title: str
    publication_year: int
    genre: str
    description: str
    author_id: int  # Важливо!


class BookResponse(BaseModel):
    id: int
    title: str
    publication_year: int
    genre: str
    description: str
    author: AuthorResponse

    class Config:
        orm_mode = True


# ==========================
#    КОРИСТУВАЧІ (Pydantic)
# ==========================
class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
