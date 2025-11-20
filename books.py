from pydantic import BaseModel


class BookCreateUpdate(BaseModel):
    title: str
    author: str
    publication_year: int | None = None
    genre: str | None = None


class BookResponse(BookCreateUpdate):
    id: int

    class Config:
        orm_mode = True  # щоб працювало з SQLAlchemy-моделлю Book
