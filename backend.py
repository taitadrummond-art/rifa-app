from flask import Flask, request
import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

conn = sqlite3.connect("rifa.db", check_same_thread=False)
c = conn.cursor()

MP_TOKEN = os.getenv("MP_ACCESS_TOKEN")

def buscar_pagamento(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {MP_TOKEN}"}
    return requests.get(url, headers=headers).json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if data.get("type") == "payment":
        payment_id = data["data"]["id"]
        pagamento = buscar_pagamento(payment_id)

        if pagamento["status"] == "approved":
            numero = int(pagamento["external_reference"])

            c.execute("UPDATE vendas SET pago=1 WHERE numero=?", (numero,))
            conn.commit()

            print(f"Pagamento confirmado: número {numero}")

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
