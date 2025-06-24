-- CREATE TABLE user(
--     userId INTEGER PRIMARY KEY AUTOINCREMENT,
--     email TEXT NOT NULL,
--     password_hash TEXT NOT NULL
--     );  

-- CREATE TABLE book(
--     bookId INTEGER PRIMARY KEY AUTOINCREMENT,
--     bookTitle TEXT NOT NULL,
--     bookAuthors TEXT NOT NULL,
--     bookDescription TEXT NOT NULL,
--     bookPrice float NOT NULL,
--     bookCover TEXT NOT NULL,
--     bookGenre TEXT NOT NULL
-- ); 

-- Tabela de Pedidos (Orders)
-- Representa um pedido geral, seja um carrinho ativo ou um pedido finalizado.
CREATE TABLE orderr (
    orderId INTEGER PRIMARY KEY AUTOINCREMENT,
    userId INTEGER NOT NULL,
    orderStatus TEXT DEFAULT 'pending' NOT NULL, -- 'pending' (carrinho), 'completed', 'cancelled', etc.
    orderDate DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (userId) REFERENCES user(userId)
);

-- Tabela de Itens do Pedido (Order Items)
-- Armazena os livros e suas quantidades dentro de um 'orderr' específico.
-- Isso serve tanto para o carrinho quanto para os pedidos finalizados.
CREATE TABLE orderItem (
    orderItemId INTEGER PRIMARY KEY AUTOINCREMENT,
    orderId INTEGER NOT NULL,
    bookId INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1 NOT NULL,
    itemPrice REAL NOT NULL, -- Armazena o preço do livro no momento da adição/compra
    FOREIGN KEY (orderId) REFERENCES orderr(orderId),
    FOREIGN KEY (bookId) REFERENCES book(bookId)
);

-- A tabela 'cart' e 'hass' são removidas.
-- O "carrinho" será simplesmente uma "orderr" com orderStatus = 'pending'.
-- Os itens no carrinho são os 'orderItem's associados a essa 'orderr' pendente.

