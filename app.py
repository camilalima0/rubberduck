from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from books import search, search_subject, get_book_by_id
import secrets
from server import pay
from werkzeug.security import generate_password_hash, check_password_hash
import random
import sqlite3
from cart_manager import (
    get_active_cart_for_user,
    create_new_cart,
    add_book_to_cart,
    get_cart_items_details_for_user,
    update_cart_item_quantity,
    remove_book_from_cart,
    finalize_order # New function to finalize the order
)
import logging

# Configure basic logging
logging.basicConfig(level=logging.DEBUG, # Set to DEBUG to capture all messages
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app_debug.log"), # Logs to a file
                        logging.StreamHandler() # Logs to console as well
                    ])

# Get a logger for your application
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

GENRES = [
    "sci-fi", "fiction", "romance", "mystery", "horror",
    "adventure", "biography", "history", "self-help", "true crime"
]

@app.route('/', methods = ["GET", "POST"])
def home():
    return render_template('index.html')

@app.route('/register_link', methods = ["GET", "POST"])
def register_link():
    return render_template('register.html')

@app.route('/login_link', methods = ["GET", "POST"])
def login_link():
    return render_template('login.html')

@app.route('/bookpage/<int:book_id>', methods = ["GET"])
def book_page_details(book_id):
    """
    Displays the details of a specific book based on its ID.
    """
    # Call the function from books.py to fetch the book by ID
    book = get_book_by_id(get_db_connection, book_id)

    if book:
        return render_template('bookpage.html', book=book)
    else:
        # If book not found, render an error page or redirect
        return render_template('error.html', message="Book not found."), 404

@app.route('/contact_link', methods = ["GET"])
def contact_link():
    return render_template('contact.html')

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
    if not genre:
        return render_template('search_results.html', books=[], error="Please, select a genre.")

    # Call the new function from books.py, passing the get_db_connection function
    books = search_subject(get_db_connection, genre) 

    if books:
        return render_template('search_results.html', books=books)
    else:
        return render_template('search_results.html', books=[], error=f"No books found for genre: {genre.capitalize()}.")

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
            conn.execute("INSERT INTO user (email, password_hash) VALUES (?, ?)",
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
            # Fetch user, ensure the column name matches your DB schema ('password_hash')
            user = conn.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

            if user is None:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401 # Changed to 401 for authentication failure

            # Use the corrected column name 'password_hash'
            stored_hash = user['password_hash']

            if check_password_hash(stored_hash, password):
                # Login successful, set session variables
                session['user_id'] = user['userId']
                session['user_email'] = user['email']
                return redirect(url_for('home'))
            else:
                return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

        except Exception as e:
            # Print the actual error to your console for debugging
            print(f"Error during login: {e}")
            print(f"Stored hash in DB: {stored_hash}")
            print(f"Entered password (plain): {password}")
            print(f"Match: {check_password_hash(stored_hash, password)}")
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
    
# --- Rota para o Carrinho de Compras ---
@app.route('/cart', methods = ["GET"])
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your cart.", "info")
        # If not logged in, redirect to login page, remember current URL
        session['next_url'] = url_for('view_cart') # To redirect back to cart after login
        return redirect(url_for('login_link'))

    cart_items = get_cart_items_details_for_user(get_db_connection, user_id)
    logger.debug(f"DEBUG (view_cart): Items retrieved for cart: {cart_items}")
    logger.debug(f"DEBUG (view_cart): Number of items: {len(cart_items)}")
    
    # Calculate total price based on itemPrice * quantity
    total_price = sum(item['itemPrice'] * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

# --- Nova Rota para Adicionar Item ao Carrinho ---
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart_route():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to add items to your cart.", "info")
        session['next_url'] = request.referrer if request.referrer else url_for('home')
        return redirect(url_for('login_link'))

    book_id = request.form.get('book_id', type=int)
    quantity = request.form.get('quantity', type=int, default=1)

    if not book_id or quantity <= 0:
        flash("Invalid book ID or quantity.", "error")
        return redirect(request.referrer or url_for('home'))

    # 1. Get or Create an active order (cart) for the user
    order_id = get_active_cart_for_user(get_db_connection, user_id)
    if not order_id:
        order_id = create_new_cart(get_db_connection, user_id)
        if not order_id:
            flash("Failed to create a new cart. Please try again.", "error")
            return redirect(request.referrer or url_for('home'))

    # 2. Add the book to the order (cart)
    order_item_id = add_book_to_cart(get_db_connection, order_id, book_id, quantity)

    if order_item_id:
        flash("Book added to cart successfully!", "success")
        return redirect(url_for('view_cart')) # Redirect to the cart page
    else:
        flash("Failed to add book to cart. Book might not exist.", "error")
        return redirect(request.referrer or url_for('home'))

# --- Rotas para ajustar quantidade ou remover item no carrinho (AJAX) ---
@app.route('/update-cart-quantity', methods=['POST'])
def update_cart_quantity_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    order_item_id = request.json.get('orderItemId', type=int)
    new_quantity = request.json.get('quantity', type=int)

    # Validate inputs
    if not isinstance(order_item_id, int) or not isinstance(new_quantity, int) or new_quantity < 0:
        return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400

    if new_quantity == 0:
        # If quantity is 0, remove the item
        success = remove_book_from_cart(get_db_connection, order_item_id)
    else:
        # Otherwise, update the quantity
        success = update_cart_item_quantity(get_db_connection, order_item_id, new_quantity)
    
    if success:
        return jsonify({'success': True, 'message': 'Cart updated successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update cart.'}), 500

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    order_item_id = request.json.get('orderItemId', type=int)
    if not isinstance(order_item_id, int):
        return jsonify({'success': False, 'message': 'Invalid order item ID.'}), 400

    success = remove_book_from_cart(get_db_connection, order_item_id)
    if success:
        return jsonify({'success': True, 'message': 'Item removed from cart successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Failed to remove item.'}), 500

# --- Rota para finalizar o carrinho (simular checkout) ---
@app.route('/checkout', methods=['POST'])
def checkout_route():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to complete your purchase.", "info")
        session['next_url'] = url_for('view_cart')
        return redirect(url_for('login_link'))
    
    # Get the current active cart for the user
    order_id = get_active_cart_for_user(get_db_connection, user_id)
    
    if not order_id:
        flash("Your cart is empty!", "warning")
        return redirect(url_for('view_cart'))
    
    # In a real application, you'd process payment here
    # For now, we'll just finalize the order status
    if finalize_order(get_db_connection, order_id):
        flash("Your order has been placed successfully!", "success")
        # Redirect to a confirmation page or home
        return redirect(url_for('home')) # Or a dedicated order confirmation page
    else:
        flash("Failed to finalize your order. Please try again.", "error")
        return redirect(url_for('view_cart'))

if __name__ == '__main__':
    logger.info("Starting Flask app...") # This will appear in the log file
    app.run(debug=True, host='0.0.0.0', use_reloader=False)


#invenção de moda:
#colocar icone de numero de itens no carrinho
#funco cinza com card nas paginas de input
#strapi