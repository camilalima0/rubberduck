import sqlite3
import requests
import random

API_KEY = 'AIzaSyCLAhnzzjKGAwpUu7N6DLUJpgzTPsGQeyQ'  # Replace with your actual API key
DB_NAME = 'rubberduck.db'

# Genres to fetch books from
GENRES = [
    "science fiction", "fiction", "romance", "mystery",
    "horror", "adventure", "biography", "history",
    "psychology", "true crime"
]


def fetch_books_by_genre(genre):
    url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&key={API_KEY}&maxResults=10"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching books for genre '{genre}': {response.status_code}")
        return []

    data = response.json()
    books = []

    for item in data.get("items", []):
        volume = item.get("volumeInfo", {})

        book = {
            "title": volume.get("title", "Title not found"),
            "authors": ", ".join(volume.get("authors", ["Unknown author"])),
            "description": volume.get("description", "No description available."),
            "cover": volume.get("imageLinks", {}).get("thumbnail", ""),
            "price": float(f"{random.randint(1, 10) * 10 - 0.10:.2f}"),  # e.g., 9.90, 19.90, ..., 99.90
            "genre": genre
        }

        books.append(book)

    return books

def insert_books(books):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for book in books:
        try:
            cursor.execute("""
                INSERT INTO book (bookTitle, bookAuthors, bookDescription, bookCover, bookPrice, bookGenre)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                book["title"],
                book["authors"],
                book["description"],
                book["cover"],
                book["price"],
                book["genre"]
            ))
            print(f"Inserted book: {book['title']} (${book['price']})")
        except sqlite3.Error as e:
            print(f"Error inserting book: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    for genre in GENRES:
        print(f"Fetching books for genre: {genre}")
        books = fetch_books_by_genre(genre)
        insert_books(books)
    print("Finished populating the database.")

def print_books():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT bookTitle, bookPrice FROM book")
    rows = cursor.fetchall()
    print("\nBooks in database:")
    for row in rows:
        print(f"{row[0]} - ${row[1]}")
    conn.close()

if __name__ == "__main__":
    for genre in GENRES:
        print(f"Fetching books for genre: {genre}")
        books = fetch_books_by_genre(genre)
        insert_books(books)
    print_books()


