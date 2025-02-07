from flask import Flask, render_template

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

@app.route('/fiction', methods = ["GET"])
def fiction():
    #filtrar no banco de dados para exibir os livros do genero ficcao
    return render_template('fiction.html')

if __name__ == '__main__':
    app.run(debug = True)