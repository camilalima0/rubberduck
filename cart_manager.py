import sqlite3

def get_active_cart_for_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT orderId FROM orderr WHERE userId = ? AND orderStatus = 'pending' ORDER BY orderDate DESC LIMIT 1",
        (user_id,)
    )
    cart = cursor.fetchone()
    return cart['orderId'] if cart else None

def create_new_cart(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orderr (userId, orderStatus) VALUES (?, 'pending')",
        (user_id,)
    )
    conn.commit()
    return cursor.lastrowid

def add_book_to_cart(conn, order_id, book_id, quantity): # Recebe a conexão 'conn'
    # Primeiro, verifique se o livro existe e obtenha seu preço
    cursor = conn.cursor()
    cursor.execute("SELECT bookPrice FROM book WHERE bookId = ?", (book_id,))
    book_data = cursor.fetchone()
    if not book_data:
        return None # Livro não encontrado

    book_price = book_data['bookPrice']

    # Verifique se o item já existe no carrinho para o livro e order_id
    cursor.execute("SELECT orderItemId, quantity FROM orderItem WHERE orderId = ? AND bookId = ?",
                   (order_id, book_id))
    existing_item = cursor.fetchone()

    if existing_item:
        # Se existe, atualiza a quantidade e o preço total
        new_quantity = existing_item['quantity'] + quantity
        item_total_price = new_quantity * book_price
        cursor.execute("UPDATE orderItem SET quantity = ?, itemTotalPrice = ? WHERE orderItemId = ?",
                       (new_quantity, item_total_price, existing_item['orderItemId']))
        conn.commit()
        return existing_item['orderItemId']
    else:
        # Se não existe, adiciona um novo item
        item_total_price = quantity * book_price
        cursor.execute("INSERT INTO orderItem (orderId, bookId, quantity, itemTotalPrice) VALUES (?, ?, ?, ?)",
                       (order_id, book_id, quantity, item_total_price))
        conn.commit()
        return cursor.lastrowid

def get_cart_items_details_for_user(conn, user_id): # Recebe a conexão 'conn'
    cursor = conn.cursor()
    query = """
    SELECT
        oi.orderItemId,
        oi.quantity,
        oi.itemTotalPrice AS itemPrice, -- Mantenha como itemPrice para compatibilidade com o Jinja
        b.bookId,
        b.bookTitle,
        b.bookAuthors,
        b.bookPrice,
        b.bookCover
    FROM
        'order' o
    JOIN
        orderItem oi ON o.orderId = oi.orderId
    JOIN
        book b ON oi.bookId = b.bookId
    WHERE
        o.userId = ? AND o.status = 'active'
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchall()

def update_cart_item_quantity(conn, order_item_id, new_quantity): # Recebe a conexão 'conn'
    cursor = conn.cursor()
    try:
        # Primeiro, obtenha o bookId e o bookPrice do item de pedido
        cursor.execute("""
            SELECT oi.bookId, b.bookPrice
            FROM orderItem oi
            JOIN book b ON oi.bookId = b.bookId
            WHERE oi.orderItemId = ?
        """, (order_item_id,))
        item_data = cursor.fetchone()

        if not item_data:
            return False # Item do pedido não encontrado

        book_price = item_data['bookPrice']
        new_item_total_price = new_quantity * book_price

        cursor.execute("""
            UPDATE orderItem
            SET quantity = ?, itemTotalPrice = ?
            WHERE orderItemId = ?
        """, (new_quantity, new_item_total_price, order_item_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating cart item quantity: {e}")
        return False

def remove_book_from_cart(conn, order_item_id): # Recebe a conexão 'conn'
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orderItem WHERE orderItemId = ?", (order_item_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing book from cart: {e}")
        return False

def finalize_order(conn, order_id): # Recebe a conexão 'conn'
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE 'order' SET status = 'completed' WHERE orderId = ?", (order_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error finalizing order: {e}")
        return False