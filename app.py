from flask import Flask, render_template, app, request
import requests

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def home():
    return render_template('index.html')

@app.route('/register_link', methods = ["GET", "POST"])
def register_link():
    return render_template('register.html')

@app.route('/login_link', methods = ["GET", "POST"])
def login_link():
    return render_template('login.html')

#configurar envio do login

@app.route('/scifi', methods = ["GET"]) #app.route /genre > e pega no banco de dados o nome do genre que foi clicado e exibe os resultados
def scifi():
    #filtrar no banco de dados para exibir os books do genre ficcao
    return render_template('sci-fi.html')

@app.route('/bookpage', methods = ["GET"])
def bookpage():
    #filtrar pelo id do livro que a pessoa clicou
    return render_template('bookpage.html')

@app.route('/contact_link', methods = ["GET"])
def contact_link():
    return render_template('contact.html')

@app.route('/cart', methods = ["GET", "POST"])
def cart():
    return render_template('cart.html')

@app.route('/delivery', methods = ["GET", "POST"])
def delivery():
    return render_template('delivery.html')

API_GOOGLE_BOOKS = 'AIzaSyCLAhnzzjKGAwpUu7N6DLUJpgzTPsGQeyQ'

# Função para buscar informações sobre um livro
def search(query):
    # URL base da API do Google Books
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_GOOGLE_BOOKS}'

    # requesting the API
    response = requests.get(url)

    #initializing data variable:
    data = None

    # status 200 = request succeded
    if response.status_code == 200:
        print(f"Dados retornados da API: {data}")  # Log dos dados retornados
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

# Rota para a busca de books
@app.route('/search-book', methods=['GET'])
def search_books():
    query = request.args.get('query')  # Pega o valor da query
    if query:
        books = search(query)  # Chama a função para buscar o livro

        if books:
            return render_template('search_results.html', books=books)
        else:
            return render_template('search_results.html', books=[], error="Nothing found.")
    else:
        return render_template('search_results.html', books=[], error="Please, type a query.")
    
# #function to filter by genre:
def search_subject(query):
    # URL base da API do Google Books, com uso do parâmetro "subject" (assunto)
    url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{query}&key={API_GOOGLE_BOOKS}'

    # Requisição para a API
    response = requests.get(url)

    # Inicializando a variável de dados:
    data = None

    if response.status_code == 200:
        print(f"Dados retornados da API: {data}")  # Log dos dados retornados
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

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')


#invenção de moda:
#colocar icone de numero de itens no carrinho
#funco cinza com card nas paginas de input
#strapi