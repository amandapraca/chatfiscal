# ChatFiscal - Versão Final Oficial - COM MEMÓRIA INTELIGENTE + SANITIZAÇÃO

import os
import base64
import pandas as pd
import html
import re
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from agent_manager import AgentManager
import logging
import sys
from gerar_pdf import gerar_relatorio_pdf

# ═══════════════════════════════════════════════════════════════
# CONFIGURAÇÃO INICIAL
# ═══════════════════════════════════════════════════════════════

st.set_page_config(page_title="ChatFiscal", layout="wide", page_icon="🦉")
load_dotenv()

logger = logging.getLogger(__name__)

# Importa interface (com tratamento de erro)
sys.path.append(os.path.join(os.path.dirname(__file__), 'main'))
try:
    from main.interface import (
        montar_interface,
        exibir_resposta_agente,
        exibir_rodape,
        mostrar_alerta,
        mostrar_erro,
        mostrar_sucesso,
        boas_vindas,
        introducao_chatfiscal,
        exibir_dica_corujito
    )
    montar_interface()
except ImportError:
    pass

# Importa dicas inteligentes (com fallback)
try:
    from dicas_corujito import gerar_dica_corujito_inteligente
except ImportError:
    def gerar_dica_corujito_inteligente(df, contexto_empresa="", historico=None):
        return "Análise dos dados carregada com sucesso. Continue fazendo perguntas!"

# Inicializa o manager
manager = AgentManager()

# ═══════════════════════════════════════════════════════════════
# ESTILOS GLOBAIS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .dica-corujito {
        background-color: #0D1B2A;
        border: 2px solid #FFD700;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    .dica-titulo {
        color: #FFD700;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
    }
    .dica-texto {
        color: #FFD700;
        font-size: 14px;
        font-family: monospace;
        line-height: 1.6;
    }
    .resposta-agente {
        background-color: #0D1B2A;
        border-left: 4px solid #FFD700;
        padding: 12px;
        border-radius: 5px;
        margin: 10px 0;
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════
if "dados_tabulares" not in st.session_state:
    st.session_state["dados_tabulares"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "pdf_carregado" not in st.session_state:
    st.session_state["pdf_carregado"] = False
if "arquivos_carregados" not in st.session_state:
    st.session_state["arquivos_carregados"] = set()
if "ultima_selecao" not in st.session_state:
    st.session_state["ultima_selecao"] = set()
if "pdf_list" not in st.session_state:
    st.session_state["pdf_list"] = []
if "df_csv_unificado" not in st.session_state:
    st.session_state["df_csv_unificado"] = None

# ═══════════════════════════════════════════════════════════════
# CARREGAMENTO DE AVATARES
# ═══════════════════════════════════════════════════════════════
def get_base64_image(path):
    """Carrega imagem e converte para base64"""
    try:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
        else:
            logger.warning(f"Avatar não encontrado: {path}")
            return None
    except Exception as e:
        logger.error(f"Erro ao carregar: {path} - {e}")
        return None

avatar_corujito_base64 = get_base64_image('assets/mascote_corujito.png')
avatar_agente_base64 = get_base64_image('assets/avatar_agente.png')

avatar_corujito_html = f"data:image/png;base64,{avatar_corujito_base64}" if avatar_corujito_base64 else None
avatar_agente_html = f"data:image/png;base64,{avatar_agente_base64}" if avatar_agente_base64 else None

def exibir_dica_popup(dica_texto):
    """Exibe dica com o Corujito"""
    col1, col2 = st.columns([0.8, 10])
    
    with col1:
        if avatar_corujito_html:
            st.markdown(
                f'<img src="{avatar_corujito_html}" style="width:60px;height:60px;border-radius:50%;border:2px solid #FFD700;">',
                unsafe_allow_html=True
            )
        else:
            st.markdown("🦉")
    
    with col2:
        st.markdown(f"""
        <div class="dica-corujito">
            <div class="dica-titulo">💡 Dica do Corujito Fiscal:</div>
            <div class="dica-texto">{dica_texto}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TÍTULO E ABAS
# ═══════════════════════════════════════════════════════════════
st.title("ChatFiscal - Seu Assistente Fiscal Inteligente")

abas = st.tabs(["Dados & Chat", "Histórico", "Auditoria", "Memória IA", "Visualizações", "Painel"])

# ═══════════════════════════════════════════════════════════════
# ABA 0: DADOS & CHAT
# ═══════════════════════════════════════════════════════════════
with abas[0]:
    st.subheader("Upload de Arquivos")
    
    MAX_SIZE = 50 * 1024 * 1024  # 50MB
    
    arquivos = st.file_uploader(
        "Escolha seus arquivos fiscais (CSV, XML ou PDF)", 
        type=["csv", "xml", "pdf"], 
        accept_multiple_files=True
    )

    if arquivos:
        arquivos_names = {a.name for a in arquivos}
        
        if arquivos_names != st.session_state["ultima_selecao"]:
            st.session_state["ultima_selecao"] = arquivos_names
            st.session_state["dados_tabulares"] = []
            st.session_state["df_csv_unificado"] = None
            manager.arquivos_processados = set()

        arquivo_count = 0
        pdf_count = 0
        
        for arquivo in arquivos:
            nome = arquivo.name
            
            if arquivo.size > MAX_SIZE:
                st.error(f"Arquivo '{nome}' muito grande (máx 50MB)")
                continue
            
            if nome in manager.arquivos_processados:
                continue
            
            try:
                if nome.lower().endswith(".pdf"):
                    try:
                        resultado = manager.carregar_arquivo(arquivo)
                        st.info(resultado if isinstance(resultado, str) else f"PDF '{nome}' processado")
                        pdf_count += 1
                        arquivo_count += 1
                        
                        if "arquivos_carregados" not in st.session_state:
                            st.session_state["arquivos_carregados"] = set()
                        st.session_state["arquivos_carregados"].add(nome)
                    except Exception as e:
                        st.error(f"Erro PDF: {e}")

                elif nome.lower().endswith((".csv", ".xml")):
                    try:
                        df = manager.carregar_arquivo(arquivo)
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            arquivo_count += 1
                            
                            if "arquivos_carregados" not in st.session_state:
                                st.session_state["arquivos_carregados"] = set()
                            st.session_state["arquivos_carregados"].add(nome)
                    except Exception as e:
                        st.error(f"Erro: {e}")
                        
            except Exception as e:
                st.error(f"Erro: {e}")
        
        if arquivo_count > 0:
            st.success(f"{arquivo_count} arquivo(s) carregado(s)")
        
        if pdf_count > 0:
            st.session_state["pdf_carregado"] = True

    # Exibe dados
    df_unificado = None
    if st.session_state.get("dados_tabulares") and len(st.session_state["dados_tabulares"]) > 0:
        df_unificado = pd.concat(st.session_state["dados_tabulares"], ignore_index=True)
        df_unificado = df_unificado.drop_duplicates().reset_index(drop=True)
        st.session_state["df_csv_unificado"] = df_unificado
        
        with st.expander("Dados Carregados", expanded=True):
            st.dataframe(df_unificado, use_container_width=True)
            st.caption(f"Total: {len(df_unificado)} linhas | {len(df_unificado.columns)} colunas")
        
        st.markdown("---")
        try:
            with st.spinner("Corujito analisando seus dados..."):
                dica = gerar_dica_corujito_inteligente(
                    df=df_unificado,
                    contexto_empresa="SP | Comércio"
                )
                if dica:
                    exibir_dica_popup(dica)
        except Exception as e:
            logger.warning(f"Aviso na dica: {e}")
    else:
        st.info("Nenhum arquivo carregado ainda")

    st.markdown("---")
    st.subheader("Chat com o Agente Fiscal")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar conversa", use_container_width=True):
            st.session_state["past"] = []
            st.session_state["generated"] = []
            st.success("Conversa limpa!")
            st.rerun()
    with col2:
        if st.button("Limpar tudo", use_container_width=True):
            st.session_state.clear()
            manager.limpar_todos_pdfs()
            st.success("Tudo limpo!")
            st.rerun()

    st.markdown("---")

    # Histórico do chat - COM SANITIZAÇÃO
    if st.session_state["generated"]:
        st.write("Histórico da Conversa:")
        
        for i in range(len(st.session_state["generated"])):
            # ✅ SANITIZA HTML para evitar injeção
            pergunta_sanitizada = html.escape(st.session_state['past'][i])
            resposta_sanitizada = html.escape(st.session_state['generated'][i])
            
            st.markdown(
                f"""
                <div style="display:flex;justify-content:flex-end;align-items:center;margin:10px 0;">
                    <div style="background-color:#1E3A5F;padding:12px 18px;border-radius:15px;
                                max-width:70%;color:white;box-shadow:0 2px 6px rgba(0,0,0,0.3);
                                font-size:15px;line-height:1.5;">
                        {pergunta_sanitizada}
                    </div>
                    <span style="font-size:42px;margin-left:10px;">🤓</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if avatar_agente_html:
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:flex-start;margin:10px 0;">
                        <img src="{avatar_agente_html}" 
                             style="width:48px;height:48px;border-radius:50%;
                                    margin-right:12px;border:2px solid #D4AF37;
                                    box-shadow:0 2px 4px rgba(0,0,0,0.2);">
                        <div style="background-color:#0D1B2A;border-left:4px solid #FFD700;
                                    padding:12px 16px;border-radius:8px;max-width:70%;
                                    color:#FFD700;box-shadow:0 2px 6px rgba(255,215,0,0.2);
                                    font-size:15px;line-height:1.6;white-space:pre-wrap;">
                            {resposta_sanitizada}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:flex-start;margin:10px 0;">
                        <span style="font-size:48px;margin-right:10px;">👨‍💼</span>
                        <div style="background-color:#0D1B2A;border-left:4px solid #FFD700;
                                    padding:12px 16px;border-radius:8px;max-width:70%;
                                    color:#FFD700;font-size:15px;line-height:1.6;white-space:pre-wrap;">
                            {resposta_sanitizada}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ÁREA DO CHAT - COM SANITIZAÇÃO DE INPUT
    user_input = st.chat_input("Digite sua pergunta sobre os dados fiscais...")

    if user_input:
        # ✅ SANITIZA INPUT (remove tags HTML)
        user_input_limpo = re.sub(r'<[^>]+>', '', user_input).strip()
        
        if not user_input_limpo:
            st.warning("Pergunta não pode estar vazia")
        elif not (df_unificado is not None or st.session_state.get("pdf_carregado")):
            st.error("Nenhum arquivo carregado! Faça upload primeiro.")
        else:
            with st.spinner("Analisando sua pergunta..."):
                try:
                    # ✅ USA a pergunta limpa
                    resposta = manager.gerar_resposta(user_input_limpo)
                    
                    # ✅ SALVA a versão limpa
                    st.session_state["past"].append(user_input_limpo)
                    st.session_state["generated"].append(resposta)
                    
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
                    logger.error(f"Erro: {e}")
            
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# ABA 1: HISTÓRICO
# ═══════════════════════════════════════════════════════════════
with abas[1]:
    st.subheader("Histórico da Sessão Atual")
    
    if st.session_state["past"] and st.session_state["generated"]:
        for i in range(len(st.session_state["past"])):
            with st.expander(f"{i+1}. {st.session_state['past'][i][:60]}{'...' if len(st.session_state['past'][i]) > 60 else ''}"):
                st.markdown(f"**Pergunta:** {st.session_state['past'][i]}")
                st.markdown(f"**Resposta:** {st.session_state['generated'][i]}")
                st.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
    else:
        st.info("Nenhuma conversa nesta sessão")

# ═══════════════════════════════════════════════════════════════
# ABA 2: AUDITORIA FISCAL
# ═══════════════════════════════════════════════════════════════
with abas[2]:
    st.subheader("📋 Auditoria Fiscal")
    
    # Função auxiliar para detectar tipo de NF
    def detectar_tipo_nf(df):
        """Detecta se é NFe, NFSe ou Misto"""
        if df is None or df.empty:
            return "Não especificado"
        
        tem_nfe = any(col.startswith(('emit_', 'dest_', 'ide_')) or 'cfop' in col.lower() for col in df.columns)
        tem_nfse = any(col.startswith(('prestador_', 'tomador_')) or 'iss' in col.lower() for col in df.columns)
        
        if tem_nfe and tem_nfse:
            return "MISTO (NFe + NFSe)"
        elif tem_nfe:
            return "NF-e (Nota Fiscal Eletrônica)"
        elif tem_nfse:
            return "NFS-e (Nota Fiscal de Serviço)"
        else:
            return "Não especificado"
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_arquivos = len(st.session_state.get("arquivos_carregados", set()))
        st.metric("📁 Arquivos Processados", total_arquivos)
    
    with col2:
        total_registros = 0
        if st.session_state.get("dados_tabulares"):
            df_unificado = pd.concat(st.session_state["dados_tabulares"], ignore_index=True)
            total_registros = len(df_unificado)
        st.metric("📊 Registros Fiscais", total_registros)
    
    with col3:
        total_perguntas = len(st.session_state.get("past", []))
        st.metric("💬 Consultas Realizadas", total_perguntas)
    
    with col4:
        total_pdfs = len(st.session_state.get("pdf_list", []))
        st.metric("📄 Documentos PDF", total_pdfs)
    
    st.markdown("---")
    
    # Trilha de Auditoria - Histórico de Ações
    st.subheader("🔍 Trilha de Auditoria")
    
    if st.session_state.get("historico"):
        with st.expander("📜 Histórico de Consultas", expanded=True):
            for i, (pergunta, resposta) in enumerate(st.session_state["historico"], 1):
                st.markdown(f"""
                **{i}. Consulta realizada:**
                - **Pergunta:** {pergunta}
                - **Data/Hora:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
                - **Tipo:** Análise Fiscal Eletrônica
                """)
                with st.expander(f"Ver resposta completa"):
                    st.write(resposta)
                st.markdown("---")
    else:
        st.info("📭 Nenhuma consulta realizada ainda")
    
    st.markdown("---")
    
    # Arquivos Processados
    st.subheader("📁 Arquivos Processados")
    
    if st.session_state.get("arquivos_carregados"):
        df_arquivos = pd.DataFrame({
            "Arquivo": list(st.session_state["arquivos_carregados"]),
            "Tipo": [nome.split(".")[-1].upper() for nome in st.session_state["arquivos_carregados"]],
            "Status": ["✅ Processado"] * len(st.session_state["arquivos_carregados"])
        })
        st.dataframe(df_arquivos, use_container_width=True)
    else:
        st.info("📭 Nenhum arquivo carregado")
    
    st.markdown("---")
    
    # Análise de Qualidade dos Dados (COM EXPLICAÇÃO E TIPO DE NF)
    if st.session_state.get("dados_tabulares"):
        st.subheader("📊 Resumo da Análise de Qualidade")
        
        df_unificado = pd.concat(st.session_state["dados_tabulares"], ignore_index=True)
        
        # Detecta tipo de NF
        tipo_nf = detectar_tipo_nf(df_unificado)
        
        # Badge do tipo de NF
        if "MISTO" in tipo_nf:
            cor_badge = "🟡"
        elif "NF-e" in tipo_nf:
            cor_badge = "🔵"
        elif "NFS-e" in tipo_nf:
            cor_badge = "🟣"
        else:
            cor_badge = "⚪"
        
        st.markdown(f"### {cor_badge} **Tipo de Documento:** {tipo_nf}")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Campos", len(df_unificado.columns))
            st.metric("Total de Registros", len(df_unificado))
            st.metric("Registros Duplicados", df_unificado.duplicated().sum())
        
        with col2:
            # Calcula campos vazios
            total_celulas = len(df_unificado) * len(df_unificado.columns)
            campos_vazios = df_unificado.isnull().sum().sum()
            
            st.metric("Campos Vazios (Total)", f"{campos_vazios:,}")
            
            # Completude CORRETA
            completude = ((total_celulas - campos_vazios) / total_celulas * 100) if total_celulas > 0 else 0
            
            # Adiciona indicador de qualidade
            if completude >= 80:
                emoji = "🟢"
                status = "Excelente"
            elif completude >= 60:
                emoji = "🟡"
                status = "Bom"
            elif completude >= 40:
                emoji = "🟠"
                status = "Moderado"
            else:
                emoji = "🔴"
                status = "Crítico"
            
            st.metric("Completude dos Dados", f"{emoji} {completude:.1f}%", delta=status)
        
        # EXPLICAÇÃO CONTEXTUAL
        st.markdown("---")
        
        if "MISTO" in tipo_nf:
            st.info(f"""
            ℹ️ **Explicação - Dados MISTO (NFe + NFSe):**
            
            A completude de **{completude:.1f}%** é **esperada** para dados consolidados de tipos diferentes:
            
            - **NF-e** possui campos específicos (Emitente, Destinatário, CFOP, ICMS, etc.)
            - **NFS-e** possui campos específicos (Prestador, Tomador, ISS, etc.)
            - Quando consolidados, os campos exclusivos de cada tipo **ficam vazios naturalmente**
            
            **Exemplo prático:**
            - Registro NF-e: campos `prestador_*` ficam vazios (não se aplicam)
            - Registro NFS-e: campos `emit_*`, `cfop`, `icms` ficam vazios (não se aplicam)
            
            ✅ **Isso NÃO indica problema de qualidade**, apenas estruturas diferentes!
            """)
        elif completude < 80:
            st.warning(f"""
            ⚠️ **Atenção - Completude abaixo de 80%:**
            
            Campos vazios detectados: **{campos_vazios:,}** de {total_celulas:,} células
            
            **Recomendações:**
            - Verifique se os XMLs estão completos
            - Confirme se campos obrigatórios estão preenchidos
            - Considere validar na origem (sistema emissor)
            """)
        else:
            st.success(f"""
            ✅ **Qualidade Excelente!**
            
            Completude de **{completude:.1f}%** indica dados bem estruturados e completos.
            """)
        
        # Detalhamento por tipo (se for MISTO)
        if "MISTO" in tipo_nf:
            st.markdown("---")
            st.subheader("📋 Detalhamento por Tipo de Documento")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Conta registros de NFe (tem campos emit_ ou cfop)
                registros_nfe = df_unificado[df_unificado.apply(lambda row: any(pd.notna(row[col]) for col in df_unificado.columns if 'emit_' in col or col == 'cfop'), axis=1)]
                st.metric("🔵 Registros NF-e", len(registros_nfe) if not registros_nfe.empty else 0)
            
            with col2:
                # Conta registros de NFSe (tem campos prestador_)
                registros_nfse = df_unificado[df_unificado.apply(lambda row: any(pd.notna(row[col]) for col in df_unificado.columns if 'prestador_' in col), axis=1)]
                st.metric("🟣 Registros NFS-e", len(registros_nfse) if not registros_nfse.empty else 0)
    
    st.markdown("---")

    # Exportação de Relatório
    st.subheader("📥 Exportar Relatório de Auditoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
     if st.button("📄 Gerar Relatório PDF", use_container_width=True):
        if st.session_state.get("dados_tabulares"):
            try:
                with st.spinner("Gerando relatório PDF..."):
                    # Prepara dados da sessão
                    dados = {
                        "dados_tabulares": st.session_state.get("dados_tabulares", []),
                        "arquivos_carregados": st.session_state.get("arquivos_carregados", set()),
                        "past": st.session_state.get("past", []),
                        "pdf_list": st.session_state.get("pdf_list", []),
                    }
                    
                    # Gera PDF usando o módulo externo
                    pdf_bytes = gerar_relatorio_pdf(dados)
                    
                    # Botão de download
                    st.download_button(
                        label="⬇️ Download Relatório PDF",
                        data=pdf_bytes,
                        file_name=f"relatorio_auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    st.success("✅ Relatório PDF gerado com sucesso!")
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                logger.error(f"Erro ao gerar PDF: {e}")
        else:
            st.warning("⚠️ Nenhum dado disponível para gerar relatório")

    
    with col2:
        if st.button("📊 Exportar para CSV", use_container_width=True):
            if st.session_state.get("dados_tabulares"):
                df_export = pd.concat(st.session_state["dados_tabulares"], ignore_index=True)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"auditoria_fiscal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Nenhum dado disponível para exportar")



# ═══════════════════════════════════════════════════════════════
# ABA 3: MEMÓRIA INTELIGENTE
# ═══════════════════════════════════════════════════════════════
with abas[3]:
    st.subheader("🧠 Memória Inteligente (Persistente)")
    
    st.markdown("""
    Esta memória **persiste entre sessões** e usa busca semântica para 
    encontrar conversas relevantes automaticamente.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    try:
        stats = manager.obter_estatisticas_memoria()
        
        if stats:
            with col1:
                st.metric("Total de Conversas", stats.get("total_registros", 0))
            with col2:
                st.metric("Vetores FAISS", stats.get("total_vetores_faiss", 0))
            with col3:
                tamanho_mb = stats.get("tamanho_indice_mb", 0)
                st.metric("Tamanho Índice", f"{tamanho_mb:.2f} MB")
            
            st.markdown("---")
            
            with st.expander("📊 Detalhes Técnicos"):
                st.json(stats)
        else:
            st.info("Memória inteligente não inicializada")
    
    except Exception as e:
        st.warning(f"Erro ao obter estatísticas: {e}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📜 Histórico Completo Persistente")
    
    with col2:
        ultimos_n = st.number_input("Mostrar últimos:", min_value=5, max_value=100, value=20, step=5)
    
    try:
        historico_formatado = manager.obter_historico_conversas(ultimos_n=ultimos_n)
        
        if historico_formatado and "Nenhum" not in historico_formatado:
            st.text_area(
                "Histórico",
                historico_formatado,
                height=400,
                disabled=True
            )
        else:
            st.info("Nenhuma conversa armazenada na memória inteligente")
    
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
    
    st.markdown("---")
    
    st.subheader("🔍 Busca Semântica")
    
    consulta_busca = st.text_input(
        "Buscar conversas relacionadas a:",
        placeholder="Ex: valores de notas fiscais"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        k_resultados = st.number_input("Resultados:", min_value=1, max_value=10, value=3)
    
    with col2:
        if st.button("🔍 Buscar", use_container_width=True):
            if consulta_busca:
                try:
                    with st.spinner("Buscando..."):
                        if manager.memoria_inteligente:
                            contexto = manager.memoria_inteligente.buscar_contexto_relevante(
                                consulta_busca, 
                                k=k_resultados
                            )
                            
                            if contexto:
                                st.success(f"Encontrados {k_resultados} resultado(s) relevante(s)")
                                st.markdown(contexto)
                            else:
                                st.info("Nenhum resultado encontrado para esta busca")
                        else:
                            st.warning("Memória inteligente não disponível")
                except Exception as e:
                    st.error(f"Erro na busca: {e}")
            else:
                st.warning("Digite algo para buscar")
    
    st.markdown("---")
    
    st.subheader("⚙️ Gerenciamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Memória Inteligente", use_container_width=True, type="secondary"):
            if st.session_state.get("confirmar_limpar_memoria"):
                try:
                    manager.limpar_memoria_inteligente()
                    st.success("Memória inteligente limpa com sucesso!")
                    st.session_state["confirmar_limpar_memoria"] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao limpar: {e}")
            else:
                st.session_state["confirmar_limpar_memoria"] = True
                st.warning("⚠️ Clique novamente para CONFIRMAR a exclusão permanente!")
    
    with col2:
        if st.button("🔄 Atualizar Estatísticas", use_container_width=True):
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# ABA 4: VISUALIZAÇÕES
# ═══════════════════════════════════════════════════════════════
with abas[4]:
    st.subheader("Visualizações")
    st.info("Em desenvolvimento")

# ═══════════════════════════════════════════════════════════════
# ABA 5: PAINEL
# ═══════════════════════════════════════════════════════════════
with abas[5]:
    st.subheader("Painel Inteligente")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Status:")
        if st.session_state.get("dados_tabulares"):
            st.success("Dados carregados")
        else:
            st.warning("Sem dados")
        
        if st.session_state.get("pdf_carregado"):
            st.success("PDFs indexados")
        else:
            st.info("Sem PDFs")
    
    with col2:
        st.metric("Perguntas (Sessão)", len(st.session_state['past']))
        
        try:
            stats = manager.obter_estatisticas_memoria()
            if stats:
                st.metric("Conversas (Total)", stats.get("total_registros", 0))
        except:
            st.metric("Conversas (Total)", "N/A")

# Rodapé
try:
    exibir_rodape()
except:
    st.markdown("---")
    st.caption("ChatFiscal 2025 | Com Memória Inteligente 🧠")
