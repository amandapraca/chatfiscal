# 🧩 PARTE 1 — Imports, sessão e estrutura base
import streamlit as st
from agent_manager import AgentManager
import pandas as pd
from llm_utils import gerar_resposta_llm

# Inicialização do agente pai
manager = AgentManager()

# Configuração da página
st.set_page_config(page_title="ChatFiscal", layout="wide")

# Inicialização da sessão
if "df" not in st.session_state:
    st.session_state["df"] = None
if "historico" not in st.session_state:
    st.session_state["historico"] = []
if "arquivo_carregado" not in st.session_state:
    st.session_state["arquivo_carregado"] = False

# Criação das abas
abas = st.tabs(
    [
        "📊 Dados & Perguntas",
        "📚 Histórico",
        "🔎 Auditoria",
        "📈 Visualizações",
        "🧠 Painel Inteligente",
    ]
)


# 🧩 PARTE 4 — Upload de Arquivos e Perguntas ao Agente
with abas[0]:
    st.subheader("📊 Dados & Perguntas")

    st.markdown(
        "Envie um ou mais arquivos fiscais para análise. Aceitamos arquivos CSV ou XML."
    )

    arquivos = st.file_uploader(
        "📎 Escolha os arquivos",
        type=["csv", "xml"],
        accept_multiple_files=True,
        key="upload_arquivos_fiscais",
    )

    dfs = []
    for arquivo in arquivos:
        df_individual = manager.carregar_arquivo(arquivo)
        if isinstance(df_individual, pd.DataFrame) and not df_individual.empty:
            dfs.append(df_individual)

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        st.session_state["df"] = df
        st.session_state["arquivo_carregado"] = True

        st.success(f"✅ {len(dfs)} arquivo(s) carregado(s) com sucesso!")
        st.dataframe(df)

        # Campo de pergunta ao agente
        pergunta = st.text_input(
            "Digite uma pergunta fiscal para o agente:", key="campo_pergunta_agente"
        )

        if pergunta and st.button("Enviar", key="botao_enviar_pergunta"):
            with st.spinner("Analisando sua pergunta..."):
                resposta = gerar_resposta_llm(pergunta, st.session_state["df"])
                st.session_state["historico"].append((pergunta, resposta))
                st.markdown(f"**Resposta do agente:** {resposta}")
    else:
        st.info(
            "Nenhum arquivo carregado ainda. Você pode simular dados ou enviar arquivos reais."
        )
        st.stop()


# 🧩 PARTE 8 — Histórico de Perguntas e Respostas
with abas[1]:
    st.subheader("📚 Histórico de Perguntas")

    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    if st.session_state["historico"]:
        for i, (pergunta, resposta) in enumerate(st.session_state["historico"], 1):
            st.markdown(f"**{i}. Pergunta:** {pergunta}")
            st.markdown(f"**Resposta:** {resposta}")
            st.markdown("---")

        # Botão para limpar histórico
        if st.button("🧹 Limpar histórico", key="botao_limpar_historico"):
            st.session_state["historico"] = []
            st.success("Histórico limpo com sucesso!")

        # Exportar como .docx
        try:
            from docx import Document
            from io import BytesIO

            doc = Document()
            doc.add_heading("Relatório de Perguntas e Respostas", level=1)

            for i, (p, r) in enumerate(st.session_state["historico"], 1):
                doc.add_paragraph(f"{i}. Pergunta: {p}")
                doc.add_paragraph(f"   Resposta: {r}")
                doc.add_paragraph("")

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                label="📤 Exportar histórico como relatório (.docx)",
                data=buffer,
                file_name="relatorio_chatfiscal.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="botao_exportar_docx",
            )
        except Exception as e:
            st.warning(f"Erro ao gerar relatório: {e}")
    else:
        st.info("Nenhuma pergunta registrada ainda. Faça uma análise para começar.")
        st.stop()

# Aba: Validação
with abas[2]:
    st.header("📚 Validação")
    if st.button("Validar Arquivo"):
        resultado = manager.validar_arquivo()
        st.text(resultado)

# Aba: Respostas
with abas[3]:
    st.header("🔎 Respostas")
    pergunta = st.text_input("Faça uma pergunta sobre os dados carregados")
    if st.button("Gerar Resposta"):
        resposta = manager.gerar_resposta(pergunta)
        st.text(resposta)
