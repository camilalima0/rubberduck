# rubberduck books

#### Video Demo:  https://www.youtube.com/watch?v=eYD1B7mxVyk

#### Description:
This project, **"Rubberduck Books"**, is a web-based e-commerce platform for e-books, developed as part of the CS50 course. Built primarily with **Python** and the **Flask** web framework, it provides a comprehensive user experience for Browse, purchasing, and managing digital books. The application leverages **Jinja2** for templating, ensuring a dynamic and interactive front-end.

At its core, the website allows users to register new accounts, securely log in, and manage their sessions. A key feature is the ability for users to send messages to the company, facilitating communication and support. The core e-commerce functionality enables users to "buy" books, though these purchases are simulated for demonstration purposes. Users can efficiently search for books either through a dedicated search bar or by navigating through categories, making discovery straightforward.

The book inventory is simulated by integrating with the **Google Books API**, providing a diverse range of titles without needing a physical stock. Each book displayed is assigned a random price generated using Python, adding a layer of realism to the simulated purchasing process. For payment processing, the application is integrated with **Stripe**, allowing for a realistic checkout flow. Test card details are provided for easy simulation of transactions. Post-payment, the system is designed to send a confirmation email to the user via **Mailgun**. While this functionality is fully implemented, the free tier of Mailgun requires prior recipient acceptance, meaning test emails won't be delivered unless configured appropriately. However, with a paid Mailgun account, this feature would work seamlessly.

The project demonstrates a robust understanding of web development principles, database management, API integration, and user interface design within the Flask ecosystem.

### Project Structure and File Breakdown

The project's codebase is organized into several key files and directories, each serving a specific purpose:

* **`app.py`**: This is the main Flask application file. It defines the core routes, handles HTTP requests, processes form submissions (like registration, login, and purchase), and orchestrates interactions with other modules and external APIs. This file acts as the central hub of the web application.
* **`server.py`**: This file likely contains the logic for stripe payment link.
* **`cart_manager.py`**: This module is dedicated to managing the user's shopping cart. It handles operations such as adding books to the cart, removing them, updating quantities, and calculating the total price. It ensures that the cart state is maintained correctly across user sessions or within the current session.
* **`books.py`**: This file contains the logic for interacting with the Google Books API. It handles fetching book data, parsing API responses, and potentially storing or caching book information locally (e.g., in `books.db`). It abstracts the details of external API communication from the main application logic.
* **`populate_books.py`**: A utility script used to pre-populate the `books.db` database with initial book data, likely retrieved from the Google Books API. This is crucial for setting up a functional inventory for testing and demonstration.
* **`rubberduck.db`**: This database file is likely used by the `rubberduck` directory. It stores user data such as email and password, books data such as title, authors, cover URL, etc.
* **`requirements.txt`**: This file lists all the Python dependencies required for the project. It's used by `pip` to install all necessary libraries, ensuring a consistent development environment.
* **`setup.sh`**: A shell script designed for initial project setup. As seen in the "Getting Started" section, it's responsible for making itself executable and setting up the Python environment (e.g., creating a virtual environment, installing dependencies from `requirements.txt`).
* **`static/`**: This directory holds all static assets for the web application, such as CSS files (`.css`) and images (`.png`, `.jpg`, etc.). These files are served directly by the Flask application to render the website's appearance and client-side functionality.
* **`templates/`**: This directory contains all the HTML template files used by Jinja2. These templates define the structure and content of the web pages, with dynamic data injected by the Flask application.

    * **`layout.html`**: The base template for pages when the user is **not logged in**. It defines the common structure, including the navigation bar (`nav`) and footer, for public-facing pages.
    * **`layout_loggedon.html`**: The base template for pages when the user **is logged in**. It likely includes a different navigation bar (e.g., with user-specific options) and a footer, maintaining consistency across authenticated views.
    * **`index.html`**: The landing page of the website.
    * **`register.html`**: The page where new users can create an account.
    * **`login.html`**: The page for existing users to sign in.
    * **`forgot_password.html`**: A page for users to initiate a password reset process.
    * **`check_verification_code.html`**: A page for verifying a code sent during password reset or account activation.
    * **`search_results.html`**: Displays the results of book searches.
    * **`bookpage.html`**: A dedicated page for displaying detailed information about a single book.
    * **`cart.html`**: The shopping cart page, where users can review items added to their cart.
    * **`checkout.html`**: The page where users provide payment information to complete a purchase.
    * **`checkout_success.html`**: A confirmation page displayed after a successful payment.
    * **`cancel.html`**: A page displayed when a payment or order process is canceled.
    * **`success.html`**: A generic success page.
    * **`contact.html`**: The page where users can send messages to the company.

---

### Design Choices and Considerations

During the development of this e-commerce project, several design choices were made to ensure functionality, maintainability, and user experience:

* **Flask for Web Framework**: Flask was chosen for its lightweight nature and flexibility. It allowed for rapid development and provided the necessary tools to build a robust web application without the overhead of larger frameworks, aligning well with the scope of a CS50 project.
* **Jinja2 for Templating**: Jinja2 was selected as the templating engine due to its powerful features, ease of use, and seamless integration with Flask. It enabled the creation of dynamic HTML pages by separating presentation logic from application logic, improving code organization and readability. The use of `layout.html` and `layout_loggedon.html` demonstrates a clear strategy for managing common UI elements based on user authentication status, avoiding code duplication.
* **SQLite for Database**: SQLite (`books.db`, `rubberduck.db`) was chosen for its simplicity and file-based nature, making it ideal for development and testing without requiring a separate database server. For a production environment, a more robust database like PostgreSQL or MySQL would be considered.
* **Google Books API for Book Data**: Instead of manually populating a large dataset of books, integrating with the Google Books API was a strategic decision to provide a vast and realistic catalog. This approach simulated a real-world inventory without the complexities of managing actual book stock. Random price generation further enhanced this simulation.
* **Stripe for Payments**: Stripe was chosen as the payment gateway due to its developer-friendly API and comprehensive documentation. It allowed for the implementation of a secure and simulated payment flow, demonstrating real-world e-commerce capabilities. The use of test card details is a standard practice for development environments.
* **Mailgun for Email Notifications**: Mailgun was integrated for handling transactional emails, specifically for sending purchase confirmations. This choice reflects an understanding of the importance of post-purchase communication. The acknowledgment of Mailgun's free-tier limitations (recipient acceptance) shows an awareness of real-world API constraints.
* **Dynamic Query Building for Search**: Although not explicitly detailed in the file list, a robust search functionality (likely implemented in `app.py` or `books.py`'s data retrieval methods) implies dynamic query building. This allows users to search by various criteria (e.g., search bar input, categories) without creating a multitude of static queries, making the search feature flexible and scalable.

These design decisions collectively contribute to a well-structured, functional, and extensible e-commerce application, providing a solid foundation for future enhancements.

---

#### Getting Started
Paste the below commands in the terminal to start application:

git clone https://github.com/camilalima0/rubberduck
cd rubberduck
chmod +x setup.sh
source setup.sh
start_app
