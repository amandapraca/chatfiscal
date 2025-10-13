import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# 🔐 Carrega a chave da API do arquivo .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 📊 Função para gerar resumo dos dados
def gerar_resumo_dos_dados(df: pd.DataFrame) -> str:
    colunas_numericas = df.select_dtypes(include="number")

    resumo = f"""
Colunas e tipos:
{df.dtypes.to_string()}

Estatísticas descritivas:
{colunas_numericas.describe().to_string()}

Correlação entre variáveis:
{colunas_numericas.corr().to_string()}
"""
    return resumo

# 🤖 Função principal que chama a LLM via Gemini
def gerar_resposta_llm(pergunta: str, df: pd.DataFrame) -> str:
    try:
        model = genai.GenerativeModel("gemini-pro-latest")
        resumo_dados = gerar_resumo_dos_dados(df)

        # 🎯 Estilo de resposta
        if "(resposta curta)" in pergunta.lower():
            estilo_instrucao = "- Responda de forma direta, objetiva e concisa. Use frases curtas e vá direto ao ponto."
        else:
            estilo_instrucao = "- Seja técnico, claro e forneça uma resposta equilibrada: nem muito longa, nem muito curta."

        # 🧠 Prompt enviado à LLM
        prompt = f"""
Você é um agente fiscal inteligente chamado ChatFiscal, especializado em documentos tributários brasileiros.

Seu papel é analisar os dados fiscais enviados pelo usuário e responder perguntas com base nesses dados.

Regras de comportamento:
1. Use apenas os dados fornecidos pelo usuário no momento da pergunta
2. Responda em português brasileiro, com linguagem clara e objetiva
3. Formate valores monetários como R$ 1.234,56
4. Use emojis relevantes para tornar a resposta mais amigável
5. Se não encontrar dados suficientes, diga: "Não encontrei informações suficientes"
6. Nunca mencione que é uma IA ou que está usando arquivos
7. Mantenha a resposta curta e direta, com dados específicos
8. Se a pergunta for irrelevante, responda educadamente que não é possível ajudar
9. Sempre que possível, destaque insights fiscais úteis (ex: maiores fornecedores, produtos mais vendidos, estados com mais emissão)

Estilo de resposta:
{estilo_instrucao}

Resumo dos dados:
{resumo_dados}

Pergunta:
{pergunta}
"""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"❌ Erro ao gerar resposta: {e}"
