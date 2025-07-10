import sqlite3
import logging
logger = logging.getLogger(__name__)

def get_active_cart_for_user(conn, user_id):
    """
    Retrieves the active shopping cart (an orderr with status 'pending') for a given user.
    If multiple 'pending' orders exist (which shouldn't happen with proper logic), it takes the most recent one.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT orderId FROM orderr WHERE userId = ? AND orderStatus = 'pending' ORDER BY orderDate DESC LIMIT 1",
        (user_id,)
    )
    cart = cursor.fetchone()
    return cart['orderId'] if cart else None

def create_new_cart(conn, user_id):
    """
    Creates a new empty shopping cart (an orderr with status 'pending') for the specified user.
    Returns the new orderId.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orderr (userId, orderStatus) VALUES (?, 'pending')",
        (user_id,)
    )
    cart_id = cursor.lastrowid
    conn.commit()
    return cart_id

def add_book_to_cart(conn, order_id, book_id, quantity=1):
    """
    Adds a book to the specified cart (orderr) or updates its quantity if it already exists.
    Also captures the book's current price.
    Returns the orderItemId of the added/updated item.
    """
    cursor = conn.cursor()

    # First, get the current price of the book
    cursor.execute("SELECT bookPrice FROM book WHERE bookId = ?", (book_id,))
    book_info = cursor.fetchone()
    if not book_info:

        return None # Book not found

    item_price_at_addition = book_info['bookPrice']

    # Check if the book already exists in this specific cart (orderItem for this orderId)
    cursor.execute(
        "SELECT orderItemId, quantity FROM orderItem WHERE orderId = ? AND bookId = ?",
        (order_id, book_id)
    )
    existing_item = cursor.fetchone()

    if existing_item:
        # Update quantity if item already exists
        new_quantity = existing_item['quantity'] + quantity
        cursor.execute(
            "UPDATE orderItem SET quantity = ? WHERE orderItemId = ?",
            (new_quantity, existing_item['orderItemId'])
        )
        order_item_id = existing_item['orderItemId']
    else:
        # Insert new order item
        cursor.execute(
            "INSERT INTO orderItem (orderId, bookId, quantity, itemPrice) VALUES (?, ?, ?, ?)",
            (order_id, book_id, quantity, item_price_at_addition)
        )
        order_item_id = cursor.lastrowid
    
    conn.commit()
    return order_item_id

def recover_info_for_email(conn, order_id):
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
        JOIN
            orderr o ON o.orderId = oi.orderId
        WHERE
            o.orderId = ?
        """,
        (order_id,) # Lembre-se que é uma tupla, mesmo com um único item
    )
    return cursor.fetchall()




def get_cart_items_details_for_user(conn, user_id):
    # Adicione este log para confirmar que row_factory está sendo configurado
    logger.debug(f"Configuring row_factory for connection: {conn.row_factory}") 
    conn.row_factory = sqlite3.Row # Ensure rows are dict-like
    # Adicione este log para confirmar o valor de row_factory após a configuração
    logger.debug(f"Row_factory after setting: {conn.row_factory}") 

    cursor = conn.cursor()

    try:
        query = """
        SELECT
            oi.orderItemId,
            oi.quantity,
            b.bookPrice AS book_unit_price, 
            oi.itemPrice AS item_total_price,
            b.bookId,
            b.bookTitle,
            b.bookAuthors,
            b.bookPrice, 
            b.bookCover
        FROM
            orderr o
        JOIN
            orderItem oi ON o.orderId = oi.orderId
        JOIN
            book b ON oi.bookId = b.bookId
        WHERE
            o.userId = ? AND o.orderStatus = 'pending'
        ORDER BY
            b.bookTitle ASC
        """
        logger.debug(f"Executing cart details query for user {user_id}. Query:\n{query}")
        cursor.execute(query, (user_id,))
        items = cursor.fetchall()
        logger.debug(f"Raw items fetched for user {user_id}: {items}")

        # --- NOVO PONTO DE VERIFICAÇÃO PRINCIPAL ---
        # Verifique o tipo do primeiro item (se houver) e tente acessar por nome
        if items:
            first_item = items[0]
            logger.debug(f"Type of first item: {type(first_item)}")
            # Tenta acessar por nome para confirmar que sqlite3.Row está funcionando
            try:
                test_title = first_item['bookTitle']
                test_price = first_item['item_total_price']
                logger.debug(f"Accessing by key successful: bookTitle='{test_title}', item_total_price='{test_price}'")
            except KeyError as ke:
                logger.error(f"KeyError: Could not access item by name. This suggests row_factory might not be working: {ke}", exc_info=True)
                # Se cair aqui, row_factory não está funcionando ou o nome da coluna está errado
        else:
            logger.debug("No items fetched, so cannot test row_factory access.")
        # --- FIM DO NOVO PONTO DE VERIFICAÇÃO ---


        return items
    except Exception as e:
        logger.error(f"Error fetching cart items for user {user_id}: {e}", exc_info=True)
 # Garante que a conexão é fechada mesmo em caso de erro
        return [] # Retorna uma lista vazia em caso de erro

def get_order_items_details(conn, order_id):
    # Adicione este log para confirmar que row_factory está sendo configurado
    logger.debug(f"Configuring row_factory for connection: {conn.row_factory}") 
    conn.row_factory = sqlite3.Row # Ensure rows are dict-like
    # Adicione este log para confirmar o valor de row_factory após a configuração
    logger.debug(f"Row_factory after setting: {conn.row_factory}") 

    cursor = conn.cursor()

    try:
        query = """
        SELECT
            oi.orderItemId,
            oi.quantity,
            b.bookPrice AS book_unit_price, 
            oi.itemPrice AS item_total_price,
            b.bookId,
            b.bookTitle,
            b.bookAuthors,
            b.bookPrice, 
            b.bookCover
        FROM
            orderItem oi
        JOIN
            book b ON oi.bookId = b.bookId
        WHERE
            oi.orderId = ?
        ORDER BY
            b.bookTitle ASC
        """
        logger.debug(f"Executing order items details query for order {order_id}. Query:\n{query}")
        cursor.execute(query, (order_id,))
        items = cursor.fetchall()
        logger.debug(f"Raw items fetched for order {order_id}: {items}")

        if items:
            first_item = items[0]
            logger.debug(f"Type of first item: {type(first_item)}")
            try:
                test_title = first_item['bookTitle']
                test_price = first_item['item_total_price']
                logger.debug(f"Accessing by key successful: bookTitle='{test_title}', item_total_price='{test_price}'")
            except KeyError as ke:
                logger.error(f"KeyError: Could not access item by name. This suggests row_factory might not be working: {ke}", exc_info=True)
        else:
            logger.debug(f"No items fetched for order {order_id}.")
        return items
    except sqlite3.Error as e:
        logger.error(f"Database error in get_order_items_details for order {order_id}: {e}", exc_info=True)
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_order_items_details for order {order_id}: {e}", exc_info=True)
        return []
    
def update_cart_item_quantity(conn, order_item_id, new_quantity):
    """
    Updates the quantity of a specific item in the cart.
    Returns True if successful, False otherwise.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orderItem SET quantity = ? WHERE orderItemId = ?",
            (new_quantity, order_item_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating quantity for orderItemId {order_item_id}: {e}")
        return False
    
def clear_user_cart(conn, order_id):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orderItem SET quantity = 0 WHERE orderId = ?",
            (order_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error clearing cart {order_id}: {e}")
        return False

def update_order_status(conn, order_id, new_status):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orderr SET orderStatus = ? WHERE orderId = ?",
            (new_status, order_id)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating the status for {order_id}: {e}")
        return False

def remove_book_from_cart(conn, order_item_id):
    """
    Removes a specific orderItem from the cart (deletes it from the orderItem table).
    """
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orderItem WHERE orderItemId = ?", (order_item_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error removing order item {order_item_id}: {e}")
        return False


def finalize_order(conn, order_id):
    """
    Changes the status of a 'pending' order to 'completed'.
    This would typically happen after a successful payment.
    """
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE orderr SET orderStatus = 'completed' WHERE orderId = ? AND orderStatus = 'pending'",
            (order_id,)
        )
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was updated
    except sqlite3.Error as e:
        print(f"Error finalizing order {order_id}: {e}")
        return False
