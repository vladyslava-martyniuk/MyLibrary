from sqlalchemy import Column, Integer, String
from base import Base  # видалили ..

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    publication_year = Column(Integer)
    genre = Column(String)
    description = Column(String)