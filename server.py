import stripe
from flask import Flask, redirect

# This is your test secret API key.
stripe.api_key = 'sk_test_51R5Ra0KfrPlB87CVRjTTRXL9pDqa1yKJO8xwExBoZxvTPUFWwv28mZFizfnox7tKaryIXpmZmhWFoPlY48FeKbxs00d2L0dTGH'

app = Flask(__name__,
            static_url_path='',
            static_folder='public')

YOUR_DOMAIN = 'http://localhost:4242'

def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1R5RguKfrPlB87CVdYC58Ko8',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

