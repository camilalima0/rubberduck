from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods = ["GET", "POST"])
def home():
    return render_template('index.html')

@app.route('/register_link', methods = ["GET", "POST"])
def register_link():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug = True)