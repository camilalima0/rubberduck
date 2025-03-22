import requests

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
def search_subject(query):
    # URL base da API do Google Books, com uso do parâmetro "subject" (assunto)
    url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{query}&key={API_GOOGLE_BOOKS}'

    # Requisição para a API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        books = []

        if 'items' in data:
            for item in data['items']:
                volume_info = item['volumeInfo']

                book = {
                    'title': volume_info.get('title', 'Título não encontrado'),
                    'authors': volume_info.get('authors', ['Autor desconhecido']),
                    'publishedDate': volume_info.get('publishedDate', 'Data de publicação não disponível'),
                    'description': volume_info.get('description', 'Descrição não disponível'),
                    'cover': volume_info.get('imageLinks', {}).get('thumbnail', 'Imagem não disponível')
                }
                books.append(book)

        return books
    else:
        return None