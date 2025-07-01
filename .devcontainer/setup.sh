# .devcontainer/setup.sh
#!/bin/bash

# Define a localização do ambiente virtual
VENV_PATH="/workspaces/rubberduck/.venv"

# 1. Instalação do Stripe CLI (dependências do sistema)
echo "--- Atualizando apt e instalando dependências do Stripe CLI ---"
sudo apt update -y
sudo apt install -y curl gnupg

echo "--- Adicionando chave GPG e repositório da Stripe ---"
curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg
echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee -a /etc/apt/sources.list.d/stripe.list

echo "--- Instalando Stripe CLI via apt ---"
sudo apt update -y
sudo apt install -y stripe

# 2. Configuração e Instalação de Dependências Python
echo "--- Removendo .venv existente (se houver) ---"
rm -rf "$VENV_PATH"

echo "--- Criando novo ambiente virtual Python ---"
python3 -m venv "$VENV_PATH"

echo "--- Ativando ambiente virtual ---"
source "$VENV_PATH/bin/activate"

echo "--- Instalando Flask e Stripe via pip (dentro do venv) ---"
# O --no-cache-dir é opcional, mas ajuda a economizar espaço no Codespace
pip install --no-cache-dir flask stripe

echo "--- Setup concluído! ---"

# Não desative o venv aqui, deixe-o ativo para o usuário após a criação do Codespace