Video Demo:  https://www.youtube.com/watch?v=eYD1B7mxVyk
Description:
This project is a e-books e-commerce for CS50 course.
It's a website which allows the user to register, login, send a message to the company and "buy" books.
The user can search the books through searchbar or category.
The books are not really for sale, I used Google Books API to simulate a stock of books and I generated a random price using python.
The payments can be tested using card number "4242 4242 4242 4242", any future date and any card code in stripe API.
After the payment, mailgun should send a mail to the user (it won't happen in test because the free version of mailgun requires previous acceptance from the recipient mail, but it would work with the paid version).

Paste the below commands in the terminal to start application:

chmod +x setup.sh
source setup.sh
start_app

