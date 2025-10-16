from llm_utils import gerar_resposta_llm

def gerar_dica_corujito(df):
    """
    Analisa o DataFrame fiscal e gera uma dica personalizada com base em padrões tributários.
    Usa LLM para transformar observações técnicas em linguagem natural.
    """
    mensagens_tecnicas = []

    # CFOPs incomuns
    if "cfop" in df.columns:
        cfops_suspeitos = df[df["cfop"].isin(["1910", "3949", "0000", "9999"])]
        if not cfops_suspeitos.empty:
            mensagens_tecnicas.append("Foram encontrados CFOPs incomuns como 1910, 3949 ou 9999.")

    # CSTs de substituição tributária
    if "cst" in df.columns:
        cst_subst = df[df["cst"].isin(["060", "070", "090"])]
        if not cst_subst.empty:
            mensagens_tecnicas.append("Há registros com CSTs que indicam substituição tributária.")

    # ICMS zerado em operações internas
    if "valor_icms" in df.columns and "cfop" in df.columns:
        icms_zerado = df[(df["valor_icms"] == 0) & (df["cfop"].astype(str).str.startswith("5"))]
        if not icms_zerado.empty:
            mensagens_tecnicas.append("Existem operações internas (CFOP 5xxx) com ICMS zerado.")

    # Campos obrigatórios nulos
    campos_obrigatorios = ["cfop", "cst", "valor_total", "base_calculo"]
    campos_nulos = [col for col in campos_obrigatorios if col in df.columns and df[col].isnull().any()]
    if campos_nulos:
        mensagens_tecnicas.append(f"Os seguintes campos obrigatórios possuem valores nulos: {', '.join(campos_nulos)}.")

    # Notas fiscais duplicadas
    if "numero_nf" in df.columns:
        duplicadas = df[df.duplicated(subset=["numero_nf"], keep=False)]
        if not duplicadas.empty:
            mensagens_tecnicas.append("Foram encontradas notas fiscais duplicadas.")

    # Regras estaduais e regime tributário
    if "uf" in df.columns:
        sp_df = df[df["uf"] == "SP"]
        if not sp_df.empty and "cst" in sp_df.columns:
            if sp_df["cst"].isin(["040", "041"]).any():
                mensagens_tecnicas.append("Em SP, CSTs 040 e 041 indicam isenção. Verifique se estão corretamente aplicados.")

    if "regime_tributario" in df.columns:
        simples_df = df[df["regime_tributario"] == "Simples Nacional"]
        if not simples_df.empty and "valor_icms" in simples_df.columns:
            if simples_df["valor_icms"].gt(0).any():
                mensagens_tecnicas.append("Empresas do Simples Nacional normalmente não destacam ICMS. Verifique os valores informados.")

    # Geração da dica final com LLM
    if mensagens_tecnicas:
        prompt = "Gere uma dica fiscal amigável com base nas seguintes observações:\n" + "\n".join(mensagens_tecnicas)
        try:
            return gerar_resposta_llm(prompt, df)
        except Exception as e:
            return f"❌ Erro ao gerar resposta: {e}"
    else:
        return "✅ Nenhuma inconsistência aparente. Mas continue atento aos detalhes fiscais!"