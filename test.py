import os
import requests
from dotenv import load_dotenv # Adicione esta linha

load_dotenv() # Carrega o .env

def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox9878947fd9fb40bcb5689df652d38b90.mailgun.org/messages",
  		auth=("api", os.getenv('MAILGUN_API_KEY')),
  		data={"from": "Mailgun Sandbox <postmaster@sandbox9878947fd9fb40bcb5689df652d38b90.mailgun.org>",
			"to": "Camila Claudino de Lima <camilaclima2011@hotmail.com>",
  			"subject": "Hello Camila Claudino de Lima",
  			"text": "Congratulations Camila Claudino de Lima, you just sent an email with Mailgun! You are truly awesome!"})

if __name__ == "__main__":
    response = send_simple_message()
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    response.raise_for_status() # Isso vai levanta