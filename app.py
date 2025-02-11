from flask import Flask, render_template, app

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

@app.route('/scifi', methods = ["GET"]) #app.route /gender > e pega no banco de dados o nome do genero que foi clicado e exibe os resultados
def scifi():
    #filtrar no banco de dados para exibir os livros do genero ficcao
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


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')