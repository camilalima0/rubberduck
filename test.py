import os
import requests
from dotenv import load_dotenv # Adicione esta linha

load_dotenv() # Carrega o .env

# Altere aqui para usar sua variável de ambiente MAILGUN_API_KEY
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN') # Você precisará do domínio também para a URL

def send_simple_message():
    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages", # Use o domínio da sua variável de ambiente
        auth=("api", MAILGUN_API_KEY), # Use a API Key da sua variável de ambiente
        data={"from": f"Mailgun Sandbox <postmaster@{MAILGUN_DOMAIN}>", # Adapte o "from" também
              "to": "Camila Claudino de Lima <lovegomez11@gmail.com>",
              "subject": "Hello Camila Claudino de Lima",
              "text": "Congratulations Camila Claudino de Lima, you just sent an email with Mailgun! You are truly awesome!"})

if __name__ == "__main__":
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN:
        print("Erro: MAILGUN_API_KEY ou MAILGUN_DOMAIN não configurados no .env")
    else:
        response = send_simple_message()
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        try:
            response.raise_for_status()
            print("E-mail enviado com sucesso!")
        except requests.exceptions.HTTPError as e:
            print(f"Erro ao enviar e-mail: {e}")
            print(f"Resposta de erro do Mailgun: {response.text}")