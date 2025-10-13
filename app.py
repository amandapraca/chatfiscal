# 🧩 PARTE 1 — Imports, sessão e estrutura base
import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import unicodedata
import numpy as np
from datetime import datetime, timedelta
import random

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
abas = st.tabs([
    "📊 Dados & Perguntas",
    "📚 Histórico",
    "🔎 Auditoria",
    "📈 Visualizações",
    "🧠 Painel Inteligente"
])


# 🧩 PARTE 2 — Funções auxiliares

# 🔧 Carrega arquivos CSV ou XML
def carregar_arquivo(arquivo):
    nome = arquivo.name.lower()
    if nome.endswith(".csv"):
        return pd.read_csv(arquivo, encoding="utf-8", sep=None, engine="python")
    elif nome.endswith(".xml"):
        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
            dados = []
            for nota in root.findall(".//NFe"):
                info = {}
                for elem in nota.iter():
                    info[elem.tag] = elem.text
                dados.append(info)
            return pd.DataFrame(dados)
        except Exception as e:
            st.error(f"Erro ao ler XML: {e}")
            return None
    else:
        st.warning("Formato de arquivo não suportado.")
        return None

# 🔍 Detecta colunas com nomes alternativos
def detectar_coluna(df, alternativas):
    if df is None or df.empty:
        return None
    colunas = [unicodedata.normalize("NFKD", c).encode("ASCII", "ignore").decode("utf-8").lower() for c in df.columns]
    for termo in alternativas:
        termo_normalizado = unicodedata.normalize("NFKD", termo).encode("ASCII", "ignore").decode("utf-8").lower()
        for i, col in enumerate(colunas):
            if termo_normalizado in col:
                return df.columns[i]
    return None

# 🧠 Gera resposta fiscal com base na pergunta
def gerar_resposta_llm(pergunta, df):
    if df is None or df.empty:
        return "Nenhum dado disponível para análise."

    pergunta = pergunta.lower()

    coluna_valor = detectar_coluna(df, ["valor", "vl_total", "total", "valor_nf"])
    coluna_emitente = detectar_coluna(df, ["emitente", "fornecedor", "empresa"])
    coluna_data = detectar_coluna(df, ["data", "emissao"])
    coluna_cfop = detectar_coluna(df, ["cfop"])

    if not coluna_valor or not coluna_emitente:
        return "Não encontrei colunas de valor ou emitente no arquivo. Verifique os dados enviados."

    try:
        df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors="coerce")
    except:
        return "Erro ao converter valores numéricos."

    if "maior valor" in pergunta or "valor maior" in pergunta:
        try:
            agrupado = df.groupby(coluna_emitente)[coluna_valor].sum().sort_values(ascending=False)
            maior_emitente = agrupado.idxmax()
            maior_valor = agrupado.max()
            return f"O emitente com maior valor é **{maior_emitente}**, com R$ {maior_valor:,.2f} em notas fiscais."
        except:
            return "Não foi possível calcular o maior valor."

    if "aparece mais vezes" in pergunta or "mais frequente" in pergunta:
        try:
            frequencias = df[coluna_emitente].value_counts()
            mais_frequente = frequencias.idxmax()
            vezes = frequencias.max()
            return f"O emitente que aparece mais vezes é **{mais_frequente}**, com **{vezes} ocorrências**."
        except:
            return "Não foi possível calcular a frequência dos emitentes."

    if "quantos emitentes" in pergunta or "emitentes distintos" in pergunta:
        try:
            emitentes_unicos = df[coluna_emitente].dropna().unique()
            return f"Existem **{len(emitentes_unicos)}** emitentes distintos no arquivo."
        except:
            return "Não foi possível contar os emitentes distintos."

    if "maior nota" in pergunta or "nota mais alta" in pergunta:
        try:
            nota_max = df.loc[df[coluna_valor].idxmax()]
            valor = nota_max[coluna_valor]
            emitente = nota_max.get(coluna_emitente, "desconhecido")
            data = nota_max.get(coluna_data, "data desconhecida")
            return f"A maior nota é de R$ {valor:,.2f}, emitida por **{emitente}** em {data}."
        except:
            return "Não foi possível identificar a maior nota fiscal."

    if "total geral" in pergunta or "soma total" in pergunta:
        try:
            total = df[coluna_valor].sum()
            return f"O valor total das notas fiscais é de **R$ {total:,.2f}**."
        except:
            return "Não foi possível calcular o total geral."

    if "média por emitente" in pergunta or "valor médio" in pergunta:
        try:
            media = df.groupby(coluna_emitente)[coluna_valor].mean().sort_values(ascending=False)
            top_emitente = media.idxmax()
            top_media = media.max()
            return f"O emitente com maior média é **{top_emitente}**, com R$ {top_media:,.2f} por nota."
        except:
            return "Não foi possível calcular a média por emitente."

    if "cfop mais usado" in pergunta or "cfop mais utilizado" in pergunta:
        if coluna_cfop:
            try:
                cfop_freq = df[coluna_cfop].value_counts()
                mais_usado = cfop_freq.idxmax()
                vezes = cfop_freq.max()
                return f"O CFOP mais utilizado é **{mais_usado}**, com **{vezes} ocorrências**."
            except:
                return "Não foi possível calcular o CFOP mais utilizado."
        else:
            return "Não encontrei a coluna de CFOP no arquivo."

    if "faturamento por mês" in pergunta or "mensal" in pergunta or "por período" in pergunta:
        if coluna_data and coluna_valor:
            try:
                df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
                df_mensal = df.dropna(subset=[coluna_data, coluna_valor])
                agrupado = df_mensal.groupby(df_mensal[coluna_data].dt.to_period("M"))[coluna_valor].sum()
                resposta = "📅 Faturamento mensal:\n\n"
                for mes, valor in agrupado.items():
                    resposta += f"- {mes.strftime('%B/%Y')}: R$ {valor:,.2f}\n"
                return resposta
            except:
                return "Não foi possível calcular o faturamento mensal."
        else:
            return "Não encontrei colunas de data ou valor para calcular o faturamento por mês."

    return "Ainda estou aprendendo a responder esse tipo de pergunta. Tente reformular ou peça uma análise diferente."

# 🧩 PARTE 3 — Simulação de dados fiscais fictícios
if not st.session_state["arquivo_carregado"]:
    fornecedores = ["Alpha Ltda", "Beta S/A", "Gamma Comércio", "Delta Import", "Epsilon Serviços"]
    np.random.seed(42)
    notas = []

    for i in range(200):
        emitente = random.choice(fornecedores + [None])
        valor = round(np.random.normal(loc=5000, scale=2000), 2)
        if random.random() < 0.05:
            valor *= -1
        data = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))
        cfop = random.choice(
            ["5102", "6108", "123", "abcd", ""] if random.random() < 0.1 else ["5102", "6108", "5405"]
        )
        notas.append({
            "emitente": emitente,
            "valor": valor,
            "data": data.strftime("%Y-%m-%d"),
            "cfop": cfop
        })

    df_simulado = pd.DataFrame(notas)

    # Verifica se colunas essenciais estão presentes
    colunas_essenciais = ["emitente", "valor", "data", "cfop"]
    colunas_faltando = [col for col in colunas_essenciais if col not in df_simulado.columns]

    if colunas_faltando:
        st.warning(f"⚠️ Dados simulados estão incompletos. Faltam as colunas: {', '.join(colunas_faltando)}")
        st.stop()
    else:
        st.session_state["df"] = df_simulado
        st.session_state["arquivo_carregado"] = True


# 🧩 PARTE 4 — Upload de Arquivos e Perguntas ao Agente
with abas[0]:
    st.subheader("📊 Dados & Perguntas")

    st.markdown("Envie um ou mais arquivos fiscais para análise. Aceitamos arquivos CSV ou XML.")

    arquivos = st.file_uploader(
        "📎 Escolha os arquivos",
        type=["csv", "xml"],
        accept_multiple_files=True,
        key="upload_arquivos_fiscais"
    )

    dfs = []
    for arquivo in arquivos:
        df_individual = carregar_arquivo(arquivo)
        if df_individual is not None and not df_individual.empty:
            dfs.append(df_individual)

    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        st.session_state["df"] = df
        st.session_state["arquivo_carregado"] = True

        st.success(f"✅ {len(dfs)} arquivo(s) carregado(s) com sucesso!")
        st.dataframe(df)

        # Campo de pergunta ao agente
        pergunta = st.text_input("Digite uma pergunta fiscal para o agente:", key="campo_pergunta_agente")

        if pergunta and st.button("Enviar", key="botao_enviar_pergunta"):
            with st.spinner("Analisando sua pergunta..."):
                resposta = gerar_resposta_llm(pergunta, df)
                st.session_state["historico"].append((pergunta, resposta))
                st.markdown(f"**Resposta do agente:** {resposta}")
    else:
        st.info("Nenhum arquivo carregado ainda. Você pode simular dados ou enviar arquivos reais.")
        st.stop()


# 🧩 PARTE 5 — Auditoria Fiscal
with abas[2]:
    st.subheader("🔎 Auditoria Fiscal")

    df = st.session_state["df"]

    if df is not None and not df.empty:
        alertas = []

        coluna_valor = detectar_coluna(df, ["valor", "vl_total", "total", "valor_nf"])
        coluna_cfop = detectar_coluna(df, ["cfop"])
        coluna_emitente = detectar_coluna(df, ["emitente", "fornecedor", "empresa"])

        # Verifica valores negativos
        if coluna_valor and coluna_valor in df.columns:
            try:
                df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors="coerce")
                negativos = df[df[coluna_valor] < 0]
                if not negativos.empty:
                    alertas.append(f"{len(negativos)} notas com valor negativo.")
            except:
                alertas.append("Erro ao verificar valores negativos.")

        # Verifica CFOPs inválidos
        if coluna_cfop and coluna_cfop in df.columns:
            try:
                cfops_invalidos = df[~df[coluna_cfop].astype(str).str.match(r"^\d{4}$")]
                if not cfops_invalidos.empty:
                    alertas.append(f"{len(cfops_invalidos)} CFOPs com formato inválido.")
            except:
                alertas.append("Erro ao verificar CFOPs inválidos.")

        # Verifica emitentes vazios
        if coluna_emitente and coluna_emitente in df.columns:
            try:
                emitentes_vazios = df[df[coluna_emitente].isna()]
                if not emitentes_vazios.empty:
                    alertas.append(f"{len(emitentes_vazios)} notas sem emitente definido.")
            except:
                alertas.append("Erro ao verificar emitentes vazios.")

        # Exibe alertas
        if alertas:
            st.markdown("### ⚠️ Alertas fiscais encontrados:")
            for alerta in alertas:
                st.warning(f"• {alerta}")
        else:
            st.success("✅ Nenhum alerta crítico foi encontrado. Os dados fiscais parecem consistentes.")
    else:
        st.info("Nenhum dado disponível para auditoria. Envie um arquivo na aba 📊 Dados & Perguntas.")
        st.stop()


# 🧩 PARTE 6 — Visualizações gráficas com filtros
with abas[3]:
    st.subheader("📈 Visualizações")

    df = st.session_state["df"]

    if df is not None and not df.empty:
        coluna_data = detectar_coluna(df, ["data", "emissao"])
        coluna_valor = detectar_coluna(df, ["valor", "vl_total", "total", "valor_nf"])
        coluna_cfop = detectar_coluna(df, ["cfop"])
        coluna_emitente = detectar_coluna(df, ["emitente", "fornecedor", "empresa"])

        # Verifica se colunas essenciais existem
        if not coluna_data or not coluna_valor:
            st.warning("Colunas de data ou valor não foram encontradas no arquivo. Visualizações indisponíveis.")
            st.stop()
        else:
            try:
                df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
                df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors="coerce")
                df = df.dropna(subset=[coluna_data, coluna_valor])
            except:
                st.warning("Erro ao preparar os dados para visualização.")
                st.stop()

            # 🎛️ Filtros interativos
            st.markdown("### 🎛️ Filtros")

            # Filtro de período
            min_data = df[coluna_data].min()
            max_data = df[coluna_data].max()
            data_inicio, data_fim = st.date_input(
                "Período", [min_data, max_data], key="filtro_periodo_visualizacao"
            )

            # Filtro de CFOP
            cfops = df[coluna_cfop].dropna().unique().tolist() if coluna_cfop else []
            cfop_selecionado = st.multiselect(
                "CFOP", cfops, default=cfops, key="filtro_cfop_visualizacao"
            )

            # Filtro de Emitente
            emitentes = df[coluna_emitente].dropna().unique().tolist() if coluna_emitente else []
            emitente_selecionado = st.multiselect(
                "Emitente", emitentes, default=emitentes, key="filtro_emitente_visualizacao"
            )

            # 🔍 Aplicação dos filtros
            df_filtrado = df[
                (df[coluna_data] >= pd.to_datetime(data_inicio)) &
                (df[coluna_data] <= pd.to_datetime(data_fim))
            ]

            if coluna_cfop:
                df_filtrado = df_filtrado[df_filtrado[coluna_cfop].isin(cfop_selecionado)]
            if coluna_emitente:
                df_filtrado = df_filtrado[df_filtrado[coluna_emitente].isin(emitente_selecionado)]

            # 📊 Gráfico de faturamento mensal
            if not df_filtrado.empty:
                df_filtrado["mes"] = df_filtrado[coluna_data].dt.to_period("M").astype(str)
                agrupado = df_filtrado.groupby("mes")[coluna_valor].sum().reset_index()

                st.markdown("### 📊 Faturamento por Mês (filtrado)")
                st.bar_chart(data=agrupado, x="mes", y=coluna_valor)

                # 💾 Botão para baixar os dados filtrados
                st.download_button(
                    label="💾 Baixar dados filtrados (CSV)",
                    data=df_filtrado.to_csv(index=False).encode("utf-8"),
                    file_name="dados_filtrados.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.info("Envie um arquivo na aba 📊 Dados & Perguntas para visualizar os gráficos.")
        st.stop()


# 🧩 PARTE 7 — Painel Fiscal Inteligente
with abas[4]:
    st.subheader("🧠 Painel Fiscal Inteligente")
    st.markdown("Este painel traz insights automáticos com base nos dados fiscais carregados.")

    df = st.session_state["df"]

    if df is not None and not df.empty:
        coluna_valor = detectar_coluna(df, ["valor", "vl_total", "total", "valor_nf"])
        coluna_emitente = detectar_coluna(df, ["emitente", "fornecedor", "empresa"])
        coluna_cfop = detectar_coluna(df, ["cfop"])
        coluna_data = detectar_coluna(df, ["data", "emissao"])

        try:
            if coluna_valor:
                df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors="coerce")
            if coluna_data:
                df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
        except:
            st.warning("Erro ao preparar os dados para análise.")
            st.stop()

        # 🔹 Destaques principais
        st.markdown("### 📌 Destaques")

        if coluna_emitente and coluna_valor:
            try:
                ranking_emitente = df.groupby(coluna_emitente)[coluna_valor].sum().sort_values(ascending=False)
                if not ranking_emitente.empty:
                    top_emitente = ranking_emitente.index[0]
                    top_valor = ranking_emitente.iloc[0]
                    st.info(f"📌 O emitente com maior valor total é **{top_emitente}**, com R$ {top_valor:,.2f}.")
            except:
                st.warning("Erro ao calcular o ranking de emitentes.")

        if coluna_cfop:
            try:
                cfop_freq = df[coluna_cfop].value_counts()
                if not cfop_freq.empty:
                    cfop_top = cfop_freq.index[0]
                    st.info(f"📌 O CFOP mais utilizado é **{cfop_top}**, com {cfop_freq.iloc[0]} ocorrências.")
            except:
                st.warning("Erro ao calcular o CFOP mais utilizado.")

        if coluna_data and coluna_valor:
            try:
                df_mensal = df.dropna(subset=[coluna_data, coluna_valor]).copy()
                faturamento_mensal = df_mensal.groupby(df_mensal[coluna_data].dt.to_period("M"))[coluna_valor].sum()
                if not faturamento_mensal.empty:
                    mes_top = faturamento_mensal.idxmax().strftime("%B/%Y")
                    valor_mes_top = faturamento_mensal.max()
                    st.info(f"📌 O mês com maior faturamento foi **{mes_top}**, com R$ {valor_mes_top:,.2f}.")
            except:
                st.warning("Erro ao calcular o faturamento mensal.")

        # 🔹 Alertas fiscais
        st.markdown("### ⚠️ Inconsistências Detectadas")
        inconsistencias = []

        if coluna_valor:
            try:
                negativos = df[df[coluna_valor] < 0]
                if not negativos.empty:
                    inconsistencias.append(f"{len(negativos)} notas com valor negativo.")
            except:
                inconsistencias.append("Erro ao verificar valores negativos.")

        if coluna_cfop:
            try:
                cfop_invalidos = df[~df[coluna_cfop].astype(str).str.match(r"^\d{4}$")]
                if not cfop_invalidos.empty:
                    inconsistencias.append(f"{len(cfop_invalidos)} CFOPs com formato inválido.")
            except:
                inconsistencias.append("Erro ao verificar CFOPs inválidos.")

        if coluna_emitente:
            try:
                emitente_vazio = df[coluna_emitente].isna().sum()
                if emitente_vazio > 0:
                    inconsistencias.append(f"{emitente_vazio} notas sem emitente definido.")
            except:
                inconsistencias.append("Erro ao verificar emitentes vazios.")

        if inconsistencias:
            for item in inconsistencias:
                st.warning(f"• {item}")
        else:
            st.success("✅ Nenhuma inconsistência crítica foi detectada.")

        # 🔹 Visualizações automáticas
        st.markdown("### 📊 Ranking de Emitentes")
        if coluna_emitente and coluna_valor:
            try:
                grafico_emitente = df.groupby(coluna_emitente)[coluna_valor].sum().sort_values(ascending=False).head(10)
                st.bar_chart(grafico_emitente)
            except:
                st.warning("Erro ao gerar gráfico de emitentes.")

        st.markdown("### 📈 Evolução Mensal do Faturamento")
        if coluna_data and coluna_valor:
            try:
                grafico_mensal = df_mensal.groupby(df_mensal[coluna_data].dt.to_period("M"))[coluna_valor].sum()
                grafico_mensal.index = grafico_mensal.index.to_timestamp()
                st.line_chart(grafico_mensal)
            except:
                st.warning("Erro ao gerar gráfico de faturamento mensal.")

        # 🔹 Campo de perguntas inteligentes
        st.markdown("---")
        st.markdown("Você também pode pedir análises personalizadas:")

        sugestoes = [
            "Gerar ranking de fornecedores por valor total",
            "Identificar CFOPs mais utilizados",
            "Detectar variações mensais de faturamento",
            "Criar gráfico de distribuição de valores por nota",
            "Listar notas com possíveis inconsistências"
        ]

        for sugestao in sugestoes:
            st.markdown(f"- {sugestao}")

        comando_inteligente = st.text_input(
            "Digite uma sugestão ou análise para o agente fiscal:",
            key="campo_comando_painel"
        )

        if comando_inteligente and st.button("Executar análise", key="botao_comando_painel"):
            with st.spinner("Gerando análise fiscal..."):
                resposta_inteligente = gerar_resposta_llm(comando_inteligente, df)
                st.session_state["historico"].append((comando_inteligente, resposta_inteligente))
                st.markdown(f"**Resposta do agente:** {resposta_inteligente}")
    else:
        st.info("Nenhum dado disponível. Envie um arquivo na aba 📊 Dados & Perguntas.")
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
                key="botao_exportar_docx"
            )
        except Exception as e:
            st.warning(f"Erro ao gerar relatório: {e}")
    else:
        st.info("Nenhuma pergunta registrada ainda. Faça uma análise para começar.")
        st.stop()
