import streamlit as st
import sqlite3
import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()

TOTAL_NUMEROS = 140
VALOR = 10

conn = sqlite3.connect("rifa.db", check_same_thread=False)
c = conn.cursor()

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))
BASE_URL = os.getenv("BASE_URL")

# ---------------- LOGIN ----------------

def login(nome, senha):
    c.execute("SELECT * FROM usuarios WHERE nome=? AND senha=?", (nome, senha))
    return c.fetchone()

def criar_usuario(nome, senha):
    try:
        c.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        return True
    except:
        return False

# ---------------- PIX ----------------

def criar_pix(numero, comprador):
    pagamento = sdk.payment().create({
        "transaction_amount": VALOR,
        "description": f"Rifa número {numero}",
        "payment_method_id": "pix",
        "external_reference": str(numero),
        "notification_url": f"{BASE_URL}/webhook",
        "payer": {"email": "teste@email.com"}
    })
    return pagamento["response"]

# ---------------- APP ----------------

st.title("🎟️ Rifa Profissional")

if "logado" not in st.session_state:
    st.session_state.logado = False

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

if not st.session_state.logado:

    if menu == "Login":
        nome = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if login(nome, senha):
                st.session_state.logado = True
                st.session_state.usuario = nome
                st.rerun()
            else:
                st.error("Erro no login")

    else:
        nome = st.text_input("Novo usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Criar conta"):
            if criar_usuario(nome, senha):
                st.success("Conta criada!")
            else:
                st.error("Usuário já existe")

else:
    st.success(f"Logado como {st.session_state.usuario}")

    numero = st.number_input("Número", 1, TOTAL_NUMEROS)
    comprador = st.text_input("Comprador")

    if st.button("Gerar Pix"):
        c.execute("INSERT OR IGNORE INTO vendas (numero, comprador, vendedor) VALUES (?, ?, ?)",
                  (numero, comprador, st.session_state.usuario))
        conn.commit()

        pix = criar_pix(numero, comprador)
        qr = pix["point_of_interaction"]["transaction_data"]["qr_code_base64"]

        st.image(qr)
        st.info("Aguardando pagamento...")

    # Mostrar grid
    c.execute("SELECT numero, pago FROM vendas")
    dados = {row[0]: row[1] for row in c.fetchall()}

    st.subheader("📊 Números")
    cols = st.columns(10)

    for i in range(1, TOTAL_NUMEROS + 1):
        col = cols[(i - 1) % 10]

        if i in dados:
            if dados[i] == 1:
                cor = "green"
            else:
                cor = "orange"
        else:
            cor = "white"

        col.markdown(
            f"<div style='background:{cor};padding:5px;text-align:center;border-radius:5px'>{i}</div>",
            unsafe_allow_html=True
        )
