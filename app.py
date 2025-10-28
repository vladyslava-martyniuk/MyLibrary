from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from base import get_db, Base, engine
from models.book import Book  # явно імпортуємо з файлу
import shutil

# Створення таблиць
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.delete("/books/{book_id}")
def delete_book_endpoint(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Книга не знайдена")
    db.delete(book)
    db.commit()
    return {"message": f"Книга з ID {book_id} успішно видалена"}
MAX_FILE_SIZE = 5 * 1024**2  
ALLOWED_CONTENT_TYPES = ["application/pdf"]

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неприпустимий тип файлу. Дозволені: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл занадто великий. Максимальний розмір: {MAX_FILE_SIZE // 1024 // 1024} MB"
        )

    try:
      
        with open(f"uploads_{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не вдалося зберегти файл: {e}"
        )
    finally:
        await file.close()

    return {"filename": file.filename, "content_type": file.content_type, "size_in_bytes": file.size}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)