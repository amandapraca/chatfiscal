import streamlit as st
import time
from io import BytesIO
import os
from datetime import datetime

# 🎨 Estilo global da página
def aplicar_estilo():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #0D1B2A !important;
            }
            h1, h2, h3, h4, h5, h6, p, span, div {
                color: #FFD700 !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# 🖼️ Logo do ChatFiscal (fixo no topo)
def exibir_logo():
    with st.container():
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("assets/logo_chatfiscal.png", width=260)
        st.markdown("</div>", unsafe_allow_html=True)

# 💬 Boas-vindas como popup (toast)
def boas_vindas():
    if "boas_vindas_exibida" not in st.session_state:
        st.toast("👋 Bem-vindo(a) ao ChatFiscal! Seu parceiro inteligente para análise tributária.", icon="💼")
        st.session_state["boas_vindas_exibida"] = True

# 📢 Introdução institucional (exibe uma vez)
def introducao_chatfiscal():
    if "introducao_exibida" not in st.session_state:
        st.markdown(
            """
            <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
                <p style='color: #FFD700; font-size: 18px; font-weight: 500;'>
                    O <strong>ChatFiscal</strong> é mais que um assistente tributário — é uma inteligência fiscal que transforma dados em decisões.  
                    Ele interpreta arquivos complexos, identifica inconsistências, responde dúvidas sobre ICMS, CFOP, CST e muito mais.  
                    Tudo isso com agilidade, precisão e uma linguagem que você entende.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.session_state["introducao_exibida"] = True

# 🦉 Dica do Corujito com logo, digitação animada e botão de download
def exibir_dica_corujito(dica):
    st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("assets/mascote_corujito.png", width=80)
    with col2:
        container = st.empty()
        texto = ""
        for letra in dica:
            texto += letra
            container.markdown(
                f"""
                <div style='background-color: #0D1B2A; border: 2px solid #FFD700; padding: 12px; border-radius: 10px;'>
                    <p style='color: #FFD700; font-size: 16px; font-weight: bold;'>Dica do Corujito:</p>
                    <p style='color: #FFD700; font-size: 15px; font-family: monospace;'>{texto}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.03)

    # Botão de download direto como .txt
    buffer = BytesIO()
    buffer.write(dica.encode("utf-8"))
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar dica como .txt",
        data=buffer,
        file_name="dica_corujito.txt",
        mime="text/plain"
    )

    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

# 🧠 Resposta com avatar do agente fiscal
def exibir_resposta_agente(pergunta, resposta):
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("assets/avatar_agente.png", width=50)
    with col2:
        st.markdown(
            f"""
            <div style='background-color: #0D1B2A; border: 2px solid #FFD700; padding: 10px; border-radius: 10px; box-shadow: 0 0 10px #FFD700;'>
                <strong style='color: #FFD700;'>Agente Fiscal:</strong><br>
                <span style='color: #FFD700;'>{resposta}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# ⚠️ Pop-ups de alerta, erro e sucesso
def mostrar_alerta(mensagem):
    st.warning(f"⚠️ {mensagem}")

def mostrar_erro(mensagem):
    st.error(f"❌ {mensagem}")

def mostrar_sucesso(mensagem):
    st.success(f"✅ {mensagem}")

# 📌 Rodapé institucional com texto completo e logo ampliado
def exibir_rodape():
    st.markdown("---")
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("assets/logo_alquimistas.jpg", width=120)
    with col2:
        st.markdown(
            """
            <div style='margin-top: 6px;'>
                <p style='color: #FFD700; font-size: 16px; margin-bottom: 6px;'>
                    <strong>Projeto desenvolvido pelos Alquimistas Digitais, através da I2a2 — Instituto de Inteligência Artificial Aplicada</strong>
                </p>
                <p style='color: #FFD700; font-size: 14px; margin-bottom: 4px;'>
                    Este agente fiscal autônomo é fruto de uma iniciativa educacional que desafia alunos a criar soluções inteligentes e inovadoras.
                </p>
                <p style='color: #FFD700; font-size: 14px; margin-bottom: 4px;'>
                    Versão 1.0 — Outubro de 2025
                </p>
                <p style='color: #FFD700; font-size: 14px;'>
                    Feito com muito carinho, lógica afiada e uma pitada de criatividade.  
                    <br>© Alquimistas Digitais. Todos os direitos reservados.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# 🧩 Monta o topo da interface
def montar_interface():
    aplicar_estilo()
    exibir_logo()
    boas_vindas()
    introducao_chatfiscal()