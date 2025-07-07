@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('stripe-signature')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(f"Erro de payload inválido: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Erro de verificação de assinatura: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"Checkout session completed: {session['id']}")

        # Agora, recupere os metadados que você enviou
        order_id = session['metadata'].get('order_id')
        user_id = session['metadata'].get('user_id')
        customer_email = session['customer_details']['email'] # Ou session['customer_email']

        print(f"Order ID: {order_id}, User ID: {user_id}, Customer Email: {customer_email}")

        # **Aqui você adicionaria sua lógica para:**
        # 1. Atualizar o status do pedido no seu banco de dados para "pago" ou "completo".
        # 2. Esvaziar o carrinho do usuário com base no user_id.
        # 3. Enviar e-mails de confirmação.
        # Exemplo (substitua pela sua lógica de DB):
        # update_order_status(order_id, 'completed')
        # clear_user_cart(user_id)

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        print(f"Checkout session async payment succeeded: {session['id']}")
        # Lidar com pagamentos que podem levar tempo (ex: Boleto)
        # Atualize o status do pedido para "pago"
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        print(f"Checkout session async payment failed: {session['id']}")
        # Lidar com falha no pagamento assíncrono
        # Atualize o status do pedido para "falhou" ou "cancelado"
    else:
        print(f"Unhandled event type: {event['type']}")

    return jsonify({'status': 'success'}), 200