import sqlite3

def get_active_cart_for_user(get_db_connection_func, user_id):
    """
    Retrieves the active shopping cart (an orderr with status 'pending') for a given user.
    If multiple 'pending' orders exist (which shouldn't happen with proper logic), it takes the most recent one.
    """
    conn = get_db_connection_func()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT orderId FROM orderr WHERE userId = ? AND orderStatus = 'pending' ORDER BY orderDate DESC LIMIT 1",
        (user_id,)
    )
    cart = cursor.fetchone()
    conn.close()
    return cart['orderId'] if cart else None

def create_new_cart(get_db_connection_func, user_id):
    """
    Creates a new empty shopping cart (an orderr with status 'pending') for the specified user.
    Returns the new orderId.
    """
    conn = get_db_connection_func()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orderr (userId, orderStatus) VALUES (?, 'pending')",
        (user_id,)
    )
    cart_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cart_id

def add_book_to_cart(get_db_connection_func, order_id, book_id, quantity=1):
    """
    Adds a book to the specified cart (orderr) or updates its quantity if it already exists.
    Also captures the book's current price.
    Returns the orderItemId of the added/updated item.
    """
    conn = get_db_connection_func()
    cursor = conn.cursor()

    # First, get the current price of the book
    cursor.execute("SELECT bookPrice FROM book WHERE bookId = ?", (book_id,))
    book_info = cursor.fetchone()
    if not book_info:
        conn.close()
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
    conn.close()
    return order_item_id

def get_cart_items_details_for_user(get_db_connection_func, user_id):
    """
    Retrieves all books currently in the user's active cart, along with their details.
    This fetches information from book, orderItem, and orderr tables.
    """
    conn = get_db_connection_func()
    conn.row_factory = sqlite3.Row # Ensure rows are dict-like
    cursor = conn.cursor()

    # Join orderr, orderItem, and book to get all necessary details for the active cart
    cursor.execute(
        """
        SELECT
            b.bookId,
            b.bookTitle,
            b.bookCover,
            -- Use itemPrice from orderItem to preserve the price at the time of addition
            oi.itemPrice,
            oi.quantity,
            oi.orderItemId,
            o.orderId -- The cart's orderId
        FROM
            orderr AS o
        JOIN
            orderItem AS oi ON o.orderId = oi.orderId
        JOIN
            book AS b ON oi.bookId = b.bookId
        WHERE
            o.userId = ? AND o.orderStatus = 'pending'
        ORDER BY
            b.bookTitle ASC
        """,
        (user_id,)
    )
    items = cursor.fetchall()
    conn.close()
    return items

def update_cart_item_quantity(get_db_connection_func, order_item_id, new_quantity):
    """
    Updates the quantity of a specific item in the cart.
    Returns True if successful, False otherwise.
    """
    conn = get_db_connection_func()
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
    finally:
        conn.close()

def remove_book_from_cart(get_db_connection_func, order_item_id):
    """
    Removes a specific orderItem from the cart (deletes it from the orderItem table).
    """
    conn = get_db_connection_func()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orderItem WHERE orderItemId = ?", (order_item_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error removing order item {order_item_id}: {e}")
        return False
    finally:
        conn.close()

def finalize_order(get_db_connection_func, order_id):
    """
    Changes the status of a 'pending' order to 'completed'.
    This would typically happen after a successful payment.
    """
    conn = get_db_connection_func()
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
    finally:
        conn.close()