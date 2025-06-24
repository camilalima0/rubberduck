import sqlite3
from books import populate_books
import os # Para verificar se o banco de dados já existe

# Define o nome do seu banco de dados
DATABASE = 'rubberduck.db'

# Define a lista de gêneros
GENRES = [
    "sci-fi", "fiction", "romance", "mystery", "horror",
    "adventure", "biography", "history", "self-help", "true crime"
]

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados criando as tabelas se não existirem."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS book (
            bookId INTEGER PRIMARY KEY AUTOINCREMENT,
            bookTitle TEXT NOT NULL,
            bookAuthors TEXT NOT NULL,
            bookDescription TEXT NOT NULL,
            bookPrice REAL NOT NULL,
            bookCover TEXT NOT NULL,
            bookGenre TEXT NOT NULL
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            userId INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    print("Database initialized (tables created if they didn't exist).")

def main():
    # Verifica se o arquivo do banco de dados já existe e tem livros
    # Isso é uma heurística simples para evitar repopular um DB já preenchido.
    # Você pode refinar essa lógica, por exemplo, verificando se a tabela 'book' tem registros.
    
    # Primeira, certifique-se que o DB e as tabelas existem
    init_db()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM book")
    book_count = cursor.fetchone()[0]
    conn.close()

    if book_count > 0:
        print(f"Banco de dados '{DATABASE}' já contém {book_count} livros. Pulando a população.")
        print("Se deseja repopular, limpe a tabela 'book' manualmente ou exclua o arquivo 'rubberduck.db'.")
        return

    print("Banco de dados vazio ou não inicializado. Iniciando população...")
    
    for genre in GENRES:
        print(f"\nPopulating for genre: {genre}")
        # Chama a função populate_books do módulo books, passando a função de conexão do DB
        success = populate_books(get_db_connection, genre, target_count=200)
        if success:
            print(f"Successfully added 200 books for {genre}.")
        else:
            print(f"Could not add 200 books for {genre}. Check logs for errors.")

    print("\nDatabase population finished.")

if __name__ == '__main__':
    main()


