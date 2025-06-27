from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from books import search, search_subject, get_book_by_id
import secrets
from flask import session
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
import stripe
import os

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

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_pk_test_51RAAO12Kh4hKsxg0LxNLU3vP1a9rGeUcVfl2soBVRPPCsY9jCBC0OaH66HZkx6Gjzxsc8HWwKMB4Q91OnqDheWZE001djNF0zp")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "pk_test_sk_test_51RAAO12Kh4hKsxg074srtWdzstEtMpwOuZuFZo8DHRFclkOxUWjvBjjPAXhAB5N695vsk1htjq1AnbCUitHuiEA900mSDI1QfL")

app.config['STRIPE_PUBLIC_KEY'] = STRIPE_PUBLIC_KEY

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
    orderItemId = add_book_to_cart(get_db_connection, order_id, book_id, quantity)

    if orderItemId:
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

    orderItemId = request.json.get('orderItemId')
    new_quantity = request.json.get('quantity')

    try:
        orderItemId = int(orderItemId)
        new_quantity = int(new_quantity)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data type for orderItemId or quantity.'}), 400

    # Validate inputs
    if new_quantity < 0: # A quantidade não pode ser negativa
        return jsonify({'success': False, 'message': 'Invalid quantity provided.'}), 400
    
     # Adicione logs para depuração
    app.logger.debug(f"Attempting to update order item {orderItemId} to quantity {new_quantity} for user {user_id}")

    if new_quantity == 0:
        # If quantity is 0, remove the item
        success = remove_book_from_cart(get_db_connection, orderItemId)
    else:
        # Otherwise, update the quantity
        success = update_cart_item_quantity(get_db_connection, orderItemId, new_quantity)
    
    if success:
        cart_items = get_cart_items_details_for_user(get_db_connection, user_id)
        new_total_cart_price = sum(item['itemPrice'] * item['quantity'] for item in cart_items)
        return jsonify({
            'success': True, 
            'message': 'Cart updated successfully!',
            'new_quantity': new_quantity, # Ainda útil para o frontend atualizar o campo de quantidade
            'new_total_cart_price': new_total_cart_price # Essencial para atualizar o subtotal
        })
    else:
        app.logger.error(f"Failed to update cart for order item {orderItemId} and quantity {new_quantity}")
        return jsonify({'success': False, 'message': 'Failed to update cart.'}), 500

@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart_route():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    orderItemId = request.json.get('orderItemId')

    try:
        orderItemId = int(orderItemId)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Invalid data type for orderItemId.'}), 400

    app.logger.debug(f"Attempting to remove order item {orderItemId} for user {user_id}")

    success = remove_book_from_cart(get_db_connection, orderItemId)

    if success:
        cart_items = get_cart_items_details_for_user(get_db_connection, user_id)
        new_total_cart_price = sum(item['itemPrice'] * item['quantity'] for item in cart_items)

        return jsonify({
            'success': True, 
            'message': 'Item removed from cart successfully!',
            'new_total_cart_price': new_total_cart_price # Essencial para atualizar o subtotal
        })
    else:
        app.logger.error(f"Failed to remove order item {orderItemId}")
        return jsonify({'success': False, 'message': 'Failed to remove item.'}), 500



# --- Rota para finalizar o carrinho (simular checkout) ---
@app.route('/checkout', methods=['POST'])
def checkout_route():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor, faça login para completar sua compra.", "info")
        session['next_url'] = url_for('view_cart')
        return redirect(url_for('login_link'))
    
    order_id = get_active_cart_for_user(get_db_connection, user_id)
    
    if not order_id:
        flash("Seu carrinho está vazio!", "warning")
        return redirect(url_for('view_cart'))
    
    cart_items = get_cart_items_details_for_user(get_db_connection, user_id)

    if not cart_items:
        flash("Seu carrinho está vazio! Adicione itens antes de finalizar a compra.", "warning")
        return redirect(url_for('view_cart'))

    # Prepare line_items para a sessão de checkout do Stripe
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'brl', # Moeda (ex: 'usd', 'eur', 'brl')
                'product_data': {
                    'name': item['bookTitle'],
                    'images': [item['bookCover']] if item['bookCover'] else [], # Imagem do produto
                    'description': f"Quantidade: {item['quantity']}" # Descrição adicional
                },
                'unit_amount': int(item['itemPrice'] * 100), # Preço unitário em centavos (Stripe usa centavos)
            },
            'quantity': item['quantity'],
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url=url_for('checkout_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('checkout_cancel', _external=True),
            metadata={
                'order_id': order_id, # Passa o order_id para o webhook saber qual pedido finalizar
                'user_id': user_id, # Opcional: passa o user_id também
            }
        )
        # Redireciona o usuário para a página de checkout do Stripe
        return redirect(checkout_session.url, code=303)

    except stripe.error.StripeError as e:
        logger.error(f"Erro ao criar sessão de checkout com Stripe: {e}")
        flash(f"Ocorreu um erro ao processar seu pagamento: {e}", "error")
        return redirect(url_for('view_cart'))

# --- Rotas para sucesso e cancelamento do checkout (redirecionadas pelo Stripe) ---
@app.route('/checkout/success')
def checkout_success():
    # Esta rota é para o redirecionamento imediato do usuário após o pagamento
    # A confirmação REAL do pagamento virá do webhook (abordagem mais segura)
    session_id = request.args.get('session_id')
    if not session_id:
        flash("Sessão de pagamento inválida.", "error")
        return redirect(url_for('home'))
    
    # Em um aplicativo real, aqui você buscaria a sessão para exibir detalhes da compra
    # Porém, a finalização do pedido no DB deve ser feita pelo webhook.
    flash("Seu pedido foi realizado com sucesso! Em breve, seu ebook estará disponível.", "success")
    return render_template('checkout_success.html', session_id=session_id)

@app.route('/checkout/cancel')
def checkout_cancel():
    flash("Seu pagamento foi cancelado. Você pode tentar novamente.", "info")
    return redirect(url_for('view_cart'))

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')
    event = None

    # Obtenha o seu 'Webhook Secret' do Dashboard do Stripe
    # Este também deve ser armazenado de forma segura (variável de ambiente)
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_tCOVKFZ1c3SVPVcA6dDfhgG7b5b6hOmd")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Erro no webhook: Payload inválido: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Erro no webhook: Assinatura inválida: {e}")
        return 'Invalid signature', 400

    # Manipular os tipos de evento
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        order_id = session_data['metadata'].get('order_id')
        user_id = session_data['metadata'].get('user_id') # Se você passou user_id no metadata

        if order_id:
            logger.info(f"Webhook: Checkout Session Completed para order_id: {order_id}")
            # Finalize o pedido no seu banco de dados
            if finalize_order(get_db_connection, order_id):
                logger.info(f"Pedido {order_id} finalizado com sucesso no DB.")
                # *** LÓGICA PARA DISPONIBILIZAR O EBOOK AQUI ***
                # Exemplo: marcar o ebook como comprado para o usuário, gerar link de download, enviar email
                # Por exemplo, você pode ter uma tabela 'user_ebooks'
                # ou um campo 'is_downloadable' na tabela 'orderItem'.
                #
                # Exemplo de lógica para "disponibilizar" (apenas log):
                logger.info(f"Ebook(s) para o pedido {order_id} (usuário {user_id}) disponíveis para download.")
                # Você pode adicionar um campo 'download_link' no orderItem ou criar uma nova tabela.
                # No seu caso, já que o status está 'completed', você pode ter uma página "Meus Livros"
                # que lista os livros dos pedidos 'completed'.

                # conn = get_db_connection()
                # cursor = conn.cursor()
                # cursor.execute("UPDATE orderItem SET download_status = 'ready' WHERE orderId = ?", (order_id,))
                # conn.commit()
                # conn.close()
                # Isso seria um exemplo mais complexo de "disponibilizar". Por ora, o finalize_order já é o suficiente.
            else:
                logger.error(f"Falha ao finalizar pedido {order_id} no DB via webhook.")
        else:
            logger.warning("Webhook: 'checkout.session.completed' recebido sem 'order_id' no metadata.")

    elif event['type'] == 'payment_intent.succeeded':
        # Você pode lidar com outros eventos aqui, se precisar
        logger.info(f"Webhook: Payment Intent Succeeded para ID: {event['data']['object']['id']}")
    # ... outros tipos de eventos que você queira processar

    return 'OK', 200 # Sempre retorne 200 OK para o Stripe

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
    logger.info("Starting Flask app...") # This will appear in the log file
    app.run(debug=True, host='0.0.0.0', use_reloader=False)