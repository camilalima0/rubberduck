from flask import Flask, render_template, request, redirect, url_for, jsonify
from books import search, search_subject
from flask import session
from server import pay
from werkzeug.security import generate_password_hash, check_password_hash
import random
import sqlite3

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
    query = request.args.get("query")  # ou .form.get() se for POST
    if not query:
        return render_template("search_results.html", error="No search term provided.", books=[])

    conn = sqlite3.connect("rubberduck.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM book
        WHERE bookTitle LIKE ?
        OR bookAuthors LIKE ?
        OR bookGenre LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%"))

    books = cursor.fetchall()
    conn.close()

    return render_template("search_results.html", books=books)

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

def get_db_connection():
    conn = sqlite3.connect('rubberduck.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST']) #if user clicks on register button
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirmation = request.form['confirmation']

        # --- Validations (VERY IMPORTANT!) ---
        # 1. Verificar se os campos não estão vazios (o 'required' no HTML ajuda, mas validação no backend é essencial)        #backend verification if the fields are not empty
        if not email or not password or not confirmation:
            return "Error: Please fill all the fields.", 400

        # 2. Verificar se a senha e a confirmação são iguais
        if password != confirmation:
            return "Error: Password and Confirmation don't match.", 400

        # 3. Hash da senha (NUNCA armazene senhas em texto puro!)
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO user (email, passwordd) VALUES (?, ?)",
                           (email, hashed_password))
            conn.commit()
            # Retorna uma resposta JSON de sucesso
            return jsonify({'success': True, 'message': 'Account successfully registered!'}), 200
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'This email is already registered.'}), 409
        except Exception as e:
            # Erro mais detalhado para depuração (NÃO mostre `e` diretamente em produção)
            print(f"Erro ao registrar usuário: {e}")
            return jsonify({'success': False, 'message': 'Server Internal Error at registering.'}), 500
        finally:
            conn.close()
    
    # Se o método não for POST (o que não deveria acontecer com o JS), retorne algo genérico
    return jsonify({'success': False, 'message': 'Method non-allowed.'}), 405

@app.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Input validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'Please fill all fields.'}), 400

        conn = get_db_connection()
        try:
            # Fetch user, ensure the column name matches your DB schema ('passwordd')
            user = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

            if user is None:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401 # Changed to 401 for authentication failure

            # Use the corrected column name 'passwordd'
            stored_hash = user['passwordd']

            if check_password_hash(stored_hash, password):
                # Login successful, set session variables
                session['user_id'] = user['id']
                session['user_email'] = user['email']
                return jsonify({'success': True, 'message': 'Login successful!'}), 200
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

        except Exception as e:
            # Print the actual error to your console for debugging
            print(f"Error during login: {e}")
            return jsonify({'success': False, 'message': 'Server internal error during login.'}), 500
        finally:
            conn.close()

    return jsonify({'success': False, 'message': 'Method not allowed.'}), 405

@app.context_processor
def inject_layout():
    """Injects the base template based on login status."""
    if 'user_id' in session:
        return dict(base_template='layout_loggedon.html')
    else:
        return dict(base_template='layout.html')

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')


#invenção de moda:
#colocar icone de numero de itens no carrinho
#funco cinza com card nas paginas de input
#strapi