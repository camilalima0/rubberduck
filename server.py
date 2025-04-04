from flask import Flask, redirect

app = Flask(__name__)

PAYMENT_LINK = 'https://buy.stripe.com/test_bIY2aQ5qC38EePe288'

def pay():
    return redirect(PAYMENT_LINK)


