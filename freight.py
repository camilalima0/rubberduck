import requests
from flask import request, jsonify

def calculate_freight():
    # Parâmetros obrigatórios para a API de Preços
    url = "https://api.correios.com.br/preco/v1/nacional/03220"  # Código de serviço: SEDEX, por exemplo
    params = {
        "nCdServico": "40010",  # Código do serviço (Ex: SEDEX)
        # "sCepOrigem": "request.args.get('postal_code_i')",
        "sCepOrigem": "13403-704",
        "sCepDestino": request.args.get('postal_code_f'),
        # "nVlPeso": request.args.get('weight'),
        "nVlPeso": "1",
        "nCdFormato": "1",  # Formato do pacote (1 = caixa/pacote)
        # "nVlComprimento": request.args.get('length'),
        "nVlComprimento": "20",
        # "nVlAltura": request.args.get('height'),
        "nVlAltura": "10",
        # "nVlLargura": request.args.get('width'),
        "nVlLargura": "5",
        "nVlDiametro": "0",
        "sCdMaoPropria": "N",
        "nVlValorDeclarado": "0",
        "sCdAvisoRecebimento": "N",
        "StrRetorno": "json"
    }
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3NDE4MTQzMDMsImlzcyI6InRva2VuLXNlcnZpY2UiLCJleHAiOjE3NDE5MDA3MDMsImp0aSI6IjVhM2E1MjM5LTViNTEtNDBjYS04NzdiLTQ5YTM1YzQ1MDYzZiIsImFtYmllbnRlIjoiUFJPRFVDQU8iLCJwZmwiOiJQRiIsImlwIjoiMTkyLjE4OS4xMjkuMjMsIDE5Mi4xNjguMS4xMzAiLCJjYXQiOiJJZDAiLCJjcGYiOiI0ODQ2MTM1NDg5MyIsImlkIjoiY2FtaWxhZGVsaW1hMCJ9.kw7raHSzmK60Sx4EYMY2nY16quelklAwWVQ3-Amp7kz2djfBlNpPdJhNfgYjOdqPZK0RkzVMXXArBbxo0MBAuEB_wWY-tLTbm-xj_E8AskvyIRFyZclEWdH4OM2ESI3HE_xdv_NHZQm8cPob8SqSryRL96k2P9n8jb5c3MNVnfKGGSembGdsCZxCiuMBUXdPHhWOm8h4q3PRm_FtIWg9_AmOBYwxOAs9kAUDZ7f2p6LM2f83Eil8yBdyApsLwL4EmaZQhU1L8HL61qmfoxcahtdFw31t-XpcFti9IXP3NKFcsUr6jYbL26DjtqyEDJYFjLxeV5zQyotfFmcwHv1oJQ"
}

     # Enviando a requisição para a API dos Correios
    response = requests.get(url, headers=headers, params=params)

    # Verificando a resposta
    if response.status_code == 200:
        return jsonify(response.json())  # Retorna os dados recebidos da API
    else:
        return jsonify({"erro": "It wasn't possible to calculate the freight cost.", "status": response.status_code}), 400   
    
