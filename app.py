from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import json
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
    update_order_status,
    clear_user_cart
)

import logging
import stripe
import os
import requests
from dotenv import load_dotenv # Adicione esta linha

try:
    with open('devcontainer.json', 'r') as f:
        dados_do_json = json.load(f)
    print("Dados carregados do JSON:")
    print(dados_do_json)

    # Agora você pode usar 'dados_do_json' no seu aplicativo
    # Por exemplo, se for um dicionário:
    # nome = dados_do_json.get('nome')
    # print(f"Nome: {nome}")

except FileNotFoundError:
    print("Erro: O arquivo 'devcontainer.json' não foi encontrado.")
except json.JSONDecodeError:
    print("Erro: O arquivo 'devcontainer.json' não é um JSON válido.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")

load_dotenv() # Carrega o .env

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

# global variables
COMPANY_EMAIL = os.environ.get("COMPANY_EMAIL")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

stripe.api_key = STRIPE_SECRET_KEY 
app.config['STRIPE_PUBLISHABLE_KEY'] = STRIPE_PUBLISHABLE_KEY
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN') 
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', f"Mailgun <postmaster@{MAILGUN_DOMAIN}>")

if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, SENDER_EMAIL]):
    logger.warning("Mailgun credential uncompleted. The email sending might fail.")

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

@app.route('/search-by-genre', methods=['GET'])
def search_by_genre():
    genre = request.args.get('genre')  
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

        if not email or not password or not confirmation:
            return "Error: Please fill all the fields.", 400

        if password != confirmation:
            return "Error: Password and Confirmation don't match.", 400

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

@app.route('/logoff', methods=['GET'])
def logoff():
    session.clear() 
    return render_template('index.html')

@app.context_processor
def inject_layout():
    """Injects the base template based on login status."""
    if 'user_id' in session:
        return dict(base_template='layout_loggedon.html')
    else:
        return dict(base_template='layout.html')
    

def send_verification_code_email(recipient_email,verification_code):
    logger.debug(f"Trying to send email via Mailgun API to {recipient_email}'")

    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, SENDER_EMAIL]):
        logger.error("Mailgun credentials uncompleted. Email not sent.")
        return False

    email_subject = "Rubberduck Books: Verification Code"
    
    html_body = f"""
    <html>
        <head></head>
        <body>
            <p>Hello!</p>
            <p>Your verification code for password recovering in <b>Rubberduck Books</b> is:</p>
            <h2 style="color: #007bff; text-align: center; font-size: 24px; letter-spacing: 3px;">{verification_code}</h2>
            <p>Please, paste this code in the website to redefine your password.</p>
            <p>This code is valid for a limited time.</p>
            <p>If you didn't request a password recovering, please ignore this email.</p>
            <p>Kind regards,</p>
            <p>Rubberduck Books</p>
        </body>
    </html>
    """

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": SENDER_EMAIL,
                "to": recipient_email,
                "subject": email_subject,
                "html": html_body
            },
        )
        response.raise_for_status() 
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Mailgun error response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpeted error sending email to {recipient_email}: {e}", exc_info=True)
        return False
    
@app.route('/send_recovery_code', methods=['POST'])
def send_recovery_code_route():
    user_email = request.form.get('email')
    
    if not user_email:
        return jsonify({'success': False, 'message': 'Please, enter your email.'}), 400

    conn = get_db_connection()
    try:
        user = get_user_by_email(conn, user_email)
        if not user:
            return jsonify({'success': True, 'message': 'If email is registered, the verification code has been sent.'}), 200

        verification_code = f"{random.randint(0, 999999):06d}"

        session['recovery_email'] = user_email
        session['recovery_code'] = verification_code

        email_sent = send_verification_code_email(user_email, verification_code)

        if email_sent:
            return jsonify({'success': True, 'message': 'The verification code has been sent to your email.'}), 200
        else:
            return jsonify({'success': False, 'message': 'Error at sending the verification code o your email. Try again.'}), 500
    except Exception as e:
        logger.error(f"Error in recovering code sending to{user_email}: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Internal server error.'}), 500
    finally:
        if conn:
            conn.close()

def update_user_password(conn, user_id, new_password_hash):
# Função auxiliar para atualizar a senha do usuário
    try:
        conn.execute("UPDATE user SET password_hash = ? WHERE userId = ?",
                        (new_password_hash, user_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating password for user {user_id}: {e}")
        return False
    
@app.route('/recover_password_page', methods=['GET'])
def recover_password_page():
    return render_template('forgot_password.html')
    
@app.route('/reset_password', methods=['POST'])
def reset_password_route():
    user_email = request.form.get('email') 
    submitted_code = request.form.get('verification_code')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not all([user_email, submitted_code, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'Please, fill all the fields.'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': "The passwords don't match."}), 400
    
    if len(new_password) < 6: 
        return jsonify({'success': False, 'message': 'The new password might have at least 6 charactres.'}), 400

    stored_email = session.get('recovery_email')
    stored_code = session.get('recovery_code')

    if not stored_email or not stored_code:
        return jsonify({'success': False, 'message': 'Session expired. Try again.'}), 400
    
    if user_email != stored_email:
        return jsonify({'success': False, 'message': "The email doesn't match the recovering session."}), 400

    if submitted_code != stored_code:
        return jsonify({'success': False, 'message': 'Wrong verification code.'}), 400

    conn = get_db_connection()
    try:
        user = get_user_by_email(conn, user_email)
        if not user:
            return jsonify({'success': False, 'message': 'User not found.'}), 404
        
        hashed_new_password = generate_password_hash(new_password)
        success = update_user_password(conn, user['userId'], hashed_new_password)

        if success:
            session.pop('recovery_email', None)
            session.pop('recovery_code', None)
            return jsonify({'success': True, 'message': 'Password successfully recovered. Now you can log in!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Error updating password to database.'}), 500

    except Exception as e:
        logger.error(f"Error redefining password to {user_email}: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Internal server error.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/cart', methods = ["GET"])
def view_cart():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your cart.", "info")
        session['next_url'] = url_for('view_cart')
        return redirect(url_for('login_link'))

    conn = get_db_connection() # Abre a conexão aqui
    try:
        # Passa a conexão (conn) para a função do cart_manager
        cart_items = get_cart_items_details_for_user(conn, user_id)
        logger.debug(f"DEBUG (view_cart): Items retrieved for cart: {cart_items}")
        logger.debug(f"DEBUG (view_cart): Number of items: {len(cart_items)}")
        
        total_price = sum(item['item_total_price'] * item['quantity'] for item in cart_items)
        
        return render_template('cart.html', cart_items=cart_items, total_price=total_price)
    finally:
        conn.close() # Fecha a conexão

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

    conn = get_db_connection() 
    try:
        order_id = get_active_cart_for_user(conn, user_id)
        if not order_id:
            order_id = create_new_cart(conn, user_id) 
            if not order_id:
                flash("Failed to create a new cart. Please try again.", "error")
                return redirect(request.referrer or url_for('home'))

        # 2. Add the book to the order (cart)
        orderItemId = add_book_to_cart(conn, order_id, book_id, quantity) 

        if orderItemId:
            flash("Book added to cart successfully!", "success")
            return redirect(url_for('view_cart'))
        else:
            flash("Failed to add book to cart. Book might not exist.", "error")
            return redirect(request.referrer or url_for('home'))
    finally:
        conn.close() 

@app.route('/update-cart-quantity', methods=['POST'])
def update_cart_quantity_route():
    logger.debug("Received request to update cart quantity.")
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    orderItemId_str = request.json.get('orderItemId') 
    new_quantity_str = request.json.get('quantity') 

    try:
        orderItemId = int(orderItemId_str)
        new_quantity = int(new_quantity_str)
    except (TypeError, ValueError):
        logger.error(f"Invalid data type received. orderItemId: {orderItemId_str}, quantity: {new_quantity_str}. Returning 400.")
        return jsonify({'success': False, 'message': 'Invalid data provided. Expected integers.'}), 400

    logger.debug(f"Update Cart: orderItemId={orderItemId}, new_quantity={new_quantity}")

    if new_quantity < 0:
        logger.error(f"Invalid quantity: {new_quantity}. Quantity cannot be negative. Returning 400.")
        return jsonify({'success': False, 'message': 'Quantity cannot be negative.'}), 400
    
    conn = get_db_connection() 
    try:
        if new_quantity == 0:
            logger.debug(f"Quantity is 0 for orderItemId {orderItemId}. Attempting to remove item.")
            success = remove_book_from_cart(conn, orderItemId) 
        else:
            logger.debug(f"Updating quantity for orderItemId {orderItemId} to {new_quantity}.")
            success = update_cart_item_quantity(conn, orderItemId, new_quantity) 
        
        if success:
            cart_items = get_cart_items_details_for_user(conn, user_id)
            new_total_cart_price = sum(item['item_total_price'] * item['quantity'] for item in cart_items) if cart_items else 0.0

            new_item_price = 0.0
            for item in cart_items:
                if item['orderItemId'] == orderItemId:
                    new_item_price = item['item_total_price'] * item['quantity']
                    break

            logger.debug(f"Cart updated successfully. new_item_price: {new_item_price}, new_total_cart_price: {new_total_cart_price}")
            return jsonify({
                'success': True, 
                'message': 'Cart updated successfully!',
                'new_quantity': new_quantity,
                'new_item_price': new_item_price, 
                'new_total_cart_price': new_total_cart_price
            })
        else:
            logger.error(f"Failed to update cart for order item {orderItemId} and quantity {new_quantity}")
            return jsonify({'success': False, 'message': 'Failed to update cart.'}), 500
    except Exception as e:
        logger.exception(f"Exception occurred during cart quantity update for orderItemId {orderItemId}: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
    finally:
        conn.close() 

@app.route('/contact_link', methods = ["GET"])
def contact_link():
    return render_template('contact.html')

def send_contact_email(user_email, user_name, message):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, SENDER_EMAIL]):
        return False

    email_subject = "Rubberduck Books: User Contact"
                                
    html_body = f"""
        <html>
            <head></head>
                <body>
                    <p>{message}</p>
                    <p>Kind regards,</p>
                    <p>{user_name}</p>
                </body>
                    </html>
                        """

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": SENDER_EMAIL,
                "to": COMPANY_EMAIL,
                "subject": email_subject,
                "html": html_body,
                "cc": user_email
                },
        )
        return True

    except requests.exceptions.RequestException as e:
            logger.error(f"Error sending email via Mailgun API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Mailgun error response: {e.response.text}")
                return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to: {e}", exc_info=True)
        return False

@app.route('/send_contact_email', methods=['POST'])
def contact_email():

    user_email = request.form.get('email')
    user_name = request.form.get('name')
    message = request.form.get('message')

    conn = get_db_connection()
    try:
        email_sent = send_contact_email(user_email, user_name, message)

        if email_sent:
            return render_template('success.html'), 200
        else:
            return jsonify({'success': False, 'message': 'Error sending email.'}), 500
    except Exception as e:
        logger.error(f"Error sending email: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Internal Server Error.'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart_route():
    logger.debug("Received request to remove item from cart.")
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    orderItemId_str = request.json.get('orderItemId')

    try:
        orderItemId = int(orderItemId_str)
    except (TypeError, ValueError):
        logger.error(f"Invalid data type received for orderItemId: {orderItemId_str}. Returning 400.")
        return jsonify({'success': False, 'message': 'Invalid order item ID. Expected an integer.'}), 400

    logger.debug(f"Attempting to remove order item {orderItemId} for user {user_id}")

    conn = get_db_connection() 
    try:
        success = remove_book_from_cart(conn, orderItemId) 

        if success:
            cart_items = get_cart_items_details_for_user(conn, user_id) 
            new_total_cart_price = sum(item['item_total_price'] * item['quantity'] for item in cart_items) if cart_items else 0.0

            logger.debug(f"Item removed successfully. New total price: {new_total_cart_price}")
            return jsonify({
                'success': True, 
                'message': 'Item removed from cart successfully!',
                'new_total_cart_price': new_total_cart_price
            })
        else:
            logger.error(f"Failed to remove order item {orderItemId}")
            return jsonify({'success': False, 'message': 'Failed to remove item.'}), 500
    except Exception as e:
        logger.exception(f"Exception occurred during item removal for orderItemId {orderItemId}: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500
    finally:
        conn.close() 

def get_user_by_email(conn, user_email):
    cursor = conn.cursor()
    cursor.execute("SELECT userId FROM user WHERE email = ?", (user_email,))
    result = cursor.fetchone()
    logger.debug(f"Searching userId for email {user_email}. Result: {result['userId'] if result else 'N/A'}")
    return result

def get_user_email(conn, user_id):

    cursor = conn.cursor()
    cursor.execute("SELECT email FROM user WHERE userId = ?", (user_id,))
    result = cursor.fetchone()
    logger.debug(f"Searching email for userId {user_id}. Result: {result['email'] if result else 'N/A'}")
    return result['email'] if result else None

@app.route('/checkout', methods=['POST'])
def checkout_route():
    BASE_URL = os.environ.get("CODESPACE_PUBLIC_URL")
    logger.debug("Received request to checkout.")
    user_id = session.get('user_id')
    if not user_id:
        flash("Please, log in to proceed to checkout.", "info")
        session['next_url'] = url_for('view_cart')
        return redirect(url_for('login_link'))
    
    conn = get_db_connection() 
    try:
        user_email = get_user_email(conn, user_id)
        if not user_email:
            logger.error(f"User email {user_id} not found in the database.")
            flash("We couldn't find the user information. Please, try again.", "error")
            return redirect(url_for('view_cart'))
        
        order_id = get_active_cart_for_user(conn, user_id)
        
        if not order_id:
            flash("Your cart is empty!", "warning")
            return redirect(url_for('view_cart'))
        
        cart_items = get_cart_items_details_for_user(conn, user_id) 

        if not cart_items:
            flash("Your cart is empty! Add items before proceeding to checkout.", "warning")
            return redirect(url_for('view_cart'))

        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': item['bookTitle'],
                        'images': [item['bookCover']] if item['bookCover'] else [],
                        'description': f"Quantidade: {item['quantity']}"
                    },
                    'unit_amount': int(item['book_unit_price'] * 100), # Use bookPrice, não itemPrice, para o preço unitário do produto
                },
                'quantity': item['quantity'],
            })

        logger.debug(f"Stripe line_items prepared: {line_items}") # Log para verificar line_items

        checkout_session = stripe.checkout.Session.create(
            customer_email = user_email,
            line_items=line_items,
            mode='payment',
            success_url=f"{BASE_URL}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL}/checkout/cancel",
            metadata={
                'order_id': order_id,
                'user_id': user_id,
            }
        )
        logger.debug(f"Stripe checkout session created: {checkout_session.url}") 
        return redirect(checkout_session.url, code=303)

    except stripe.error.StripeError as e:
        logger.error(f"Error creating checkout session with Stripe: {e}")
        flash(f"Error processing the payment: {e}", "error")
        return redirect(url_for('view_cart'))
    except Exception as e:
        logger.exception(f"EUnexpected error in checkout: {e}") 
        flash(f"Unexpected error: {e}", "error")
        return redirect(url_for('view_cart'))
    finally:
        if conn:
            conn.close() 

@app.route('/checkout/success')
def checkout_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash("Invalid payment session.", "error")
        return redirect(url_for('home'))
    
    flash("Request successfully completed! We'll send your product via email.", "success")
    return render_template('checkout_success.html', session_id=session_id)

@app.route('/checkout/cancel')
def checkout_cancel():
    flash("Cancelled payment. Please, try again.", "info")
    return redirect(url_for('view_cart'))

def send_ebook_email(recipient_email, order_id):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, SENDER_EMAIL]):
        return False

    conn = None 
    try:
        conn = get_db_connection() 
        conn.row_factory = sqlite3.Row 

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                b.bookTitle,
                b.bookCover
            FROM
                book b
            JOIN
                orderItem oi ON b.bookId = oi.bookId
            WHERE
                oi.orderId = ?
            """,
            (order_id,)
        )
        books_in_order = cursor.fetchall()

        if not books_in_order:
            logger.warning(f"No book found for order {order_id}. Email not sent.")
            return False

        email_subject_prefix = "Your Rubberduck e-Books: "
        book_titles_list = [book['bookTitle'] for book in books_in_order]
        email_subject = email_subject_prefix + ", ".join(book_titles_list)
        
        html_body = f"""
        <html>
            <head></head>
            <body>
                <p>Hello!</p>
                <p>Thanks for choosing Rubberduck Books. Your e-books are attached. Have fun!</p>
        """
        
        attachments = [] 

        for book in books_in_order:
            book_title = book['bookTitle']
            book_cover_url = book['bookCover'] 
            
            html_body += f"""
                <p><b>{book_title}</b></p>
                <p><img src="{book_cover_url}" alt="Capa do livro: {book_title}" style="max-width:200px; height:auto; display:block; margin: 10px 0;"></p>
            """
            
            if 'bookFile' in book and book['bookFile']:
                ebook_filepath = os.path.join(os.getcwd(), 'ebook_files', book['bookFile'])
                if os.path.exists(ebook_filepath):
                    attachments.append(("attachment", (book['bookFile'], open(ebook_filepath, 'rb'), 'application/pdf')))
                else:
                    logger.warning(f"Ebook file not found for {book_title}.")
            else:
                html_body += f"<p>Soon, you will receive a email with your e-book.</p>"

            html_body += """<hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0)); margin: 20px 0;">"""
        
        html_body += f"""
                <p>Thank you!</p>
                <p>Kind regards,</p>
                <p>Rubberduck Books</p>
            </body>
        </html>
        """

        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": SENDER_EMAIL,
                "to": recipient_email,
                "subject": email_subject,
                "html": html_body
            },
            files=attachments if attachments else None
        )
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Mailgun error response: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {recipient_email}: {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload error: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid Signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"Checkout session completed: {session['id']}")

        order_id = session['metadata'].get('order_id')
        user_id = session['metadata'].get('user_id')
        customer_email = session['customer_details']['email']

        print(f"Order ID: {order_id}, User ID: {user_id}, Customer Email: {customer_email}")

        conn = get_db_connection()
        update_order_status(conn, order_id, "completed")
        clear_user_cart(conn, order_id)

        email_sent = send_ebook_email(customer_email, order_id) 
            
        if email_sent:
            logger.info(f"Email sending process to {customer_email} started successfully .")
        else:
            logger.error(f"Fail at email sending process to {customer_email}.")
   

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        print(f"Checkout session async payment succeeded: {session['id']}")

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        print(f"Checkout session async payment failed: {session['id']}")

    else:
        print(f"Unhandled event type: {event['type']}")

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    logger.info("Starting Flask app...") 
    app.run(debug=True, host='0.0.0.0', use_reloader=False)