# checkout_simulation.py
import stripe
import os
import json

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

if not stripe.api_key:
    print("ERRO: A variável de ambiente 'STRIPE_SECRET_KEY' não está configurada.")
    print("Por favor, defina-a antes de rodar o script:")
    print("Exemplo: export STRIPE_SECRET_KEY='sk_test_sua_chave_aqui'")
    exit(1)

# --- Dados de Cliente de Teste ---
# Você pode usar um email de teste da Stripe.
# Para cartões de teste, a Stripe oferece números específicos (e.g., 4242...4242 para VISA)
# e qualquer data futura/CVC para simular diferentes cenários.
# Veja: https://stripe.com/docs/testing#cards
TEST_CUSTOMER_EMAIL = "customer@example.com"
TEST_CUSTOMER_NAME = "Teste Silva"
TEST_CUSTOMER_DESCRIPTION = "Cliente de teste para simulação de checkout"

# --- Dados do Produto/Serviço (para a sessão de checkout) ---
# Em um aplicativo real, isso viria de um banco de dados ou lógica de negócio.
PRODUCT_NAME = "Assinatura Premium"
PRODUCT_PRICE_USD_CENTS = 2000 # $20.00 em centavos
PRODUCT_QUANTITY = 1
PRODUCT_DESCRIPTION = "Acesso completo a todos os recursos premium por 1 mês"

print(f"Iniciando simulação de checkout para o cliente: {TEST_CUSTOMER_EMAIL}")

def create_and_simulate_checkout():
    try:
        # 1. Criar um Cliente Stripe (opcional para Checkout Session, mas boa prática)
        # Se o cliente já existir, a Stripe não criará um duplicado para o mesmo email
        # (se você usar search ou list para verificar antes de criar).
        # Para simplificar aqui, vamos sempre tentar criar um.
        customer = stripe.Customer.create(
            email=TEST_CUSTOMER_EMAIL,
            name=TEST_CUSTOMER_NAME,
            description=TEST_CUSTOMER_DESCRIPTION,
        )
        print(f"\nCliente Stripe criado/encontrado: {customer.id}")

        # 2. Criar uma Checkout Session
        # Esta é a maneira mais comum de lidar com pagamentos no frontend.
        # Você cria a sessão no backend e redireciona o usuário para ela.
        # Os URLs success_url e cancel_url são para onde o usuário será redirecionado
        # após concluir (ou cancelar) o pagamento na página de checkout da Stripe.
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'], # Aceita pagamentos com cartão
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': PRODUCT_NAME,
                        'description': PRODUCT_DESCRIPTION,
                    },
                    'unit_amount': PRODUCT_PRICE_USD_CENTS,
                },
                'quantity': PRODUCT_QUANTITY,
            }],
            mode='payment', # Use 'subscription' para assinaturas, 'setup' para salvar métodos de pagamento
            success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://example.com/cancel',
            customer=customer.id, # Associa o cliente à sessão de checkout
            metadata={
                'order_id': 'ORD-12345', # Exemplo de metadados para seu próprio controle
                'user_email': TEST_CUSTOMER_EMAIL
            }
        )

        print(f"\nSessão de Checkout criada com sucesso!")
        print(f"ID da Sessão: {checkout_session.id}")
        print(f"URL de Checkout (simulação): {checkout_session.url}")
        print("\n*** Para simular o checkout, copie e cole a URL acima no seu navegador. ***")
        print("Use um dos cartões de teste da Stripe para concluir o pagamento.")
        print("https://stripe.com/docs/testing#cards")
        print("\nDetalhes da Sessão:")
        print(json.dumps(checkout_session.to_dict(), indent=2))


        # Em um cenário real, você redirecionaria o usuário para checkout_session.url
        # e, após a conclusão, a Stripe enviaria um webhook para o seu servidor
        # confirmando o pagamento.

    except stripe.error.StripeError as e:
        print(f"\nErro da Stripe: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")

if __name__ == "__main__":
    create_and_simulate_checkout()