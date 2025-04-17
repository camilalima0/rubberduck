Database schema:

CREATE TABLE book(
    bookId INTEGER PRIMARY KEY AUTOINCREMENT,
    bookTitle VARCHAR(100) NOT NULL,
    bookAuthors VARCHAR(200) NOT NULL,
    bookDescription VARCHAR(500) NOT NULL,
    bookPrice float NOT NULL
);
CREATE TABLE cartItem(
    quantity INTEGER DEFAULT 1 NOT NULL,
    bookId INTEGER NOT NULL,
    cartId INTEGER NOT NULL,
    FOREIGN KEY (bookId) REFERENCES book(bookId),
    FOREIGN KEY (cartId) REFERENCES cart(cartId)
);
CREATE TABLE user(
    userId INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL,
    passwordd VARCHAR(20) NOT NULL
    );
CREATE TABLE orderr(
    orderId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    FOREIGN KEY (userId) REFERENCES user(userId)
);
CREATE TABLE cart(
    cartId INTEGER PRIMARY KEY AUTOINCREMENT,
    cartStatus INT DEFAULT 1 NOT NULL /*OPEN*/
);
CREATE TABLE orderItem(
    quantity INTEGER DEFAULT 1 NOT NULL,
    orderId INTEGER NOT NULL,
    bookId INTEGER NOT NULL,
    FOREIGN KEY (orderId) REFERENCES orderr(orderId),
    FOREIGN KEY (bookId) REFERENCES book(bookId)
);
CREATE TABLE has(
    cartId INTEGER NOT NULL,
    userId INTEGER NOT NULL,
    FOREIGN KEY (cartId) REFERENCES cart(cartId),
    FOREIGN KEY (userId) REFERENCES user(userId)
);

