from flask import Flask, render_template, request
from books import search, search_subject
from server import pay
import random

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

# Rota para buscar livros pela barra de pesquisa
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
        return render_template('search_results.html', books=[], error="Please, insert a query.")

# Rota para buscar livros por gênero (por exemplo, "fiction", "romance", etc.)
@app.route('/search-by-genre', methods=['GET'])
def search_by_genre():
    genre = request.args.get('genre')  # Pega o valor do gênero
    if genre:
        books = search_subject(genre)  # Chama a função para buscar livros por gênero
        if books:
            return render_template('search_results.html', books=books)
        else:
            return render_template('search_results.html', books=[], error="Nothing found.")
    else:
        return render_template('search_results.html', books=[], error="Please, select a genre.")

#payment:
@app.route('/pay', methods=['GET','POST'])
def create_checkout():
    return pay()

@app.route('/random-number')
def random_number():
    # Gerar um número aleatório entre 1 e 100
    random_num = random.randint(29, 99)
    return render_template('index.html', random_num=random_num)

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')


#invenção de moda:
#colocar icone de numero de itens no carrinho
#funco cinza com card nas paginas de input
#strapi