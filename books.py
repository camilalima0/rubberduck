import requests
import random
import sqlite3

GOOGLE_BOOKS_BASE_URL = "https://www.googleapis.com/books/v1/volumes"
API_GOOGLE_BOOKS = 'AIzaSyCLAhnzzjKGAwpUu7N6DLUJpgzTPsGQeyQ'

# Finds informations about a book
def search(query):
    # URL base da API do Google Books
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_GOOGLE_BOOKS}'
    # requesting the API
    response = requests.get(url)

    # status 200 = request succeded
    if response.status_code == 200:
        # Converts the answaer to JSON
        data = response.json()
        books= []

        # is there items into the answer?
        if 'items' in data:
            for item in data['items']:
                volume_info = item['volumeInfo']

                book = {
                    # Extrair informações do livro
                'title': volume_info.get('title', 'Title not found'),
                'authors': volume_info.get('authors', ['Unknown author']),
                'publishedDate': volume_info.get('publishedDate', 'Data de publicação não disponível'),
                'description': volume_info.get('description', 'Descrição não disponível'),
                'cover': volume_info.get('imageLinks', {}).get('thumbnail', 'Imagem não disponível')
                }
                books.append(book)

        return books
    else:
        return None
    
# #function to filter by genre:
def search_subject(get_db_connection_func, genre_query):
    conn = get_db_connection_func()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM book
        WHERE bookGenre LIKE ?
        ORDER BY bookTitle ASC
        """,
        (f"%{genre_query}%",)
    )

    books = cursor.fetchall()
    conn.close()
    return books
    
    
#fixing API Google books connection to database

#generating random price

def generate_random_price():
    integer_part = random.randint(9, 99)
    price = float(f"{integer_part}.90")
    return price 

def populate_books(get_db_connection_func, query_term, target_count = 200):

    books_added_for_genre = 0
    start_index = 0
    max_results_per_request = 40

    while books_added_for_genre < target_count:
        params = {
            "q": f"subject:{query_term}", # Usar "subject" para gênero
            "maxResults": max_results_per_request,
            "startIndex": start_index,
            "key": API_GOOGLE_BOOKS
        }

        try:
            response = requests.get(GOOGLE_BOOKS_BASE_URL, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar à Google Books API para '{query_term}': {e}")
            break # Sair do loop em caso de erro de conexão

        if 'items' not in data:
            print(f"Nenhum item encontrado para '{query_term}' na paginação {start_index}.")
            break # Se não houver mais itens, sair do loop

        conn = get_db_connection_func()
        cursor = conn.cursor()
        batch_added = 0

        for item in data['items']:
            if books_added_for_genre >= target_count:
                break # Já atingimos o limite para este gênero

            volume_info = item.get('volumeInfo', {})

            book_title = volume_info.get('title', 'No Title')
            book_authors = ', '.join(volume_info.get('authors', ['Unknown Author']))
            book_description = volume_info.get('description', 'No description available.')
            book_cover = volume_info.get('imageLinks', {}).get('thumbnail', 'No Cover')

            # Priorizar o gênero que estamos buscando, ou usar as categorias da API
            categories = volume_info.get('categories', [])
            book_genre = query_term # Definir o gênero principal como o da query
            if categories and query_term not in categories: # Se a query não estiver nas categorias, adicioná-la
                 book_genre = f"{query_term}, {', '.join(categories)}"
            elif categories:
                book_genre = ', '.join(categories)


            book_price = generate_random_price()

            try:
                cursor.execute(
                    """
                    INSERT INTO book (bookTitle, bookAuthors, bookDescription, bookPrice, bookCover, bookGenre)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (book_title, book_authors, book_description, book_price, book_cover, book_genre)
                )
                books_added_for_genre += 1
                batch_added += 1
            except sqlite3.IntegrityError:
                # Pode ocorrer se houver UNIQUE constraints (ex: título único), mas nossa tabela não tem.
                # Se acontecer, pode ser um item duplicado que a API retornou ou um erro inesperado.
                print(f"Livro '{book_title}' já existe ou erro de integridade. Pulando.")
                continue
            except sqlite3.Error as e:
                print(f"Erro ao inserir livro '{book_title}': {e}")
                # Não é um erro fatal para o loop, tente o próximo livro
        
        conn.commit()
        conn.close()
        
        print(f"Adicionados {batch_added} livros na iteração para '{query_term}'. Total: {books_added_for_genre}/{target_count}")

        # Se menos livros que o esperado foram adicionados no batch,
        # ou se o total de itens na resposta foi menor que max_results,
        # significa que não há mais resultados disponíveis, então saia.
        if len(data.get('items', [])) < max_results_per_request:
            print(f"Nenhum resultado novo encontrado para '{query_term}'. Parando.")
            break

        start_index += max_results_per_request # Próxima página de resultados
        
    print(f"Finalizada população para o gênero: {query_term}. Total adicionado: {books_added_for_genre}")
    return books_added_for_genre >= target_count

def get_book_by_id(get_db_connection_func, book_id):
    """
    Retrieves a single book from the local database by its ID.

    Args:
        get_db_connection_func (function): The function to get a database connection.
        book_id (int): The ID of the book to retrieve.

    Returns:
        sqlite3.Row or None: The book object if found, otherwise None.
    """
    conn = get_db_connection_func()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM book
        WHERE bookId = ?
        """,
        (book_id,)
    )

    book = cursor.fetchone() # Fetch only one result
    conn.close()
    return book