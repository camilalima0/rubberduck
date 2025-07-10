start_app() {
    python3 -m venv .venv && /bin/bash -c source .venv/bin/activate

    pip install -r requirements.txt

    curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
    ngrok authtoken ${NGROK_AUTHTOKEN} 

    curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee -a /etc/apt/sources.list.d/stripe.list sudo apt update sudo apt install stripe

    sudo apt install -y sqlite3

    flask run
    ngrok http 5000 --log=stdout > ngrok.log

}
