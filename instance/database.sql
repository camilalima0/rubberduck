-- CREATE TABLE user(
--     userId INTEGER PRIMARY KEY AUTOINCREMENT,
--     email TEXT NOT NULL,
--     passwordd TEXT NOT NULL
--     ); CRIADO

-- CREATE TABLE orderr(
--     orderId INTEGER PRIMARY KEY AUTOINCREMENT,
--     userId INTEGER NOT NULL,
--     FOREIGN KEY (userId) REFERENCES user(userId)
-- ); CRIADO

-- CREATE TABLE cart(
--     cartId INTEGER PRIMARY KEY AUTOINCREMENT,
--     cartStatus INT DEFAULT 1 NOT NULL, 
--     orderItemId INTEGER NOT NULL,
--     FOREIGN KEY (orderItemId) REFERENCES orderItem(orderItemId)
-- ); CRIADO

-- CREATE TABLE book(
--     bookId INTEGER PRIMARY KEY AUTOINCREMENT,
--     bookTitle TEXT NOT NULL,
--     bookAuthors TEXT NOT NULL,
--     bookDescription TEXT NOT NULL,
--     bookPrice float NOT NULL,
--     bookCover TEXT NOT NULL,
--     bookGenre TEXT NOT NULL
-- ); 

-- CREATE TABLE orderItem(
--     orderItemId INTEGER PRIMARY KEY AUTOINCREMENT,
--     quantity INTEGER DEFAULT 1 NOT NULL,
--     orderId INTEGER NOT NULL,
--     bookId INTEGER NOT NULL,
--     FOREIGN KEY (orderId) REFERENCES orderr(orderId),
--     FOREIGN KEY (bookId) REFERENCES book(bookId)
-- ); CRIADO

-- CREATE TABLE hass(
--     cartId INTEGER NOT NULL,
--     userId INTEGER NOT NULL,
--     FOREIGN KEY (cartId) REFERENCES cart(cartId),
--     FOREIGN KEY (userId) REFERENCES user(userId)
-- );