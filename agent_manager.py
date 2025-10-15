# agent_manager.py

from memory_module import MemoriaCompartilhada
import pandas as pd
import xml.etree.ElementTree as ET
from llm_utils import gerar_resposta_llm as llm_resposta
from file_reader import FileReader
from data_validator import DataValidator


class AgentManager:
    """
    Classe responsável por coordenar os módulos filhos e gerenciar o fluxo de dados.
    """

    def __init__(self):
        self.memoria = MemoriaCompartilhada()

    def processar_entrada(self, entrada, tipo):
        """
        Processa a entrada do usuário e delega ao módulo apropriado.
        :param entrada: Dados ou pergunta fornecida pelo usuário.
        :param tipo: Tipo de entrada (e.g., 'arquivo', 'pergunta').
        :return: Resultado do processamento.
        """
        if tipo == "arquivo":
            return self._processar_arquivo(entrada)
        elif tipo == "pergunta":
            return self._processar_pergunta(entrada)
        else:
            return "Tipo de entrada não suportado."

    def _processar_arquivo(self, arquivo):
        """
        Processa arquivos enviados pelo usuário utilizando o FileReader.
        :param arquivo: Arquivo carregado (CSV, XML, etc.).
        :return: Mensagem de status ou erro.
        """
        nome = arquivo.name.lower()
        try:
            if nome.endswith(".csv"):
                df = FileReader.carregar_csv(arquivo)
                self.memoria.salvar("arquivo_carregado", df)
                return "Arquivo CSV processado com sucesso."
            elif nome.endswith(".xml"):
                df = FileReader.carregar_xml(arquivo)
                self.memoria.salvar("arquivo_carregado", df)
                return "Arquivo XML processado com sucesso."
            else:
                return "Formato de arquivo não suportado."
        except Exception as e:
            return f"Erro ao processar arquivo: {e}"

    def _processar_pergunta(self, pergunta):
        """
        Processa perguntas enviadas pelo usuário.
        :param pergunta: Pergunta em linguagem natural.
        :return: Resposta gerada pelo módulo de respostas inteligentes.
        """
        # Aqui chamaremos o módulo de respostas inteligentes (a ser implementado)
        return "Resposta gerada pelo módulo de respostas inteligentes."

    def coordenar_modulos(self):
        """
        Coordena os módulos filhos e integra os resultados.
        :return: Resultado consolidado.
        """
        # Exemplo de coordenação entre módulos
        arquivo = self.memoria.obter("arquivo_carregado")
        if not arquivo:
            return "Nenhum arquivo carregado para processar."

        # Chamadas fictícias aos módulos filhos
        resumo = "Resumo gerado pelo módulo leitor."
        resposta = "Resposta gerada pelo módulo de respostas."

        return {"resumo": resumo, "resposta": resposta}

    def carregar_arquivo(self, arquivo):
        """
        Carrega e processa arquivos CSV ou XML.
        :param arquivo: Arquivo carregado pelo usuário.
        :return: DataFrame com os dados processados.
        """
        nome = arquivo.name.lower()
        if nome.endswith(".csv"):
            try:
                df = pd.read_csv(arquivo, encoding="utf-8", sep=None, engine="python")
                self.memoria.salvar("arquivo_carregado", df)
                return df
            except Exception as e:
                return f"Erro ao carregar arquivo CSV: {e}"
        elif nome.endswith(".xml"):
            try:
                tree = ET.parse(arquivo)
                root = tree.getroot()
                dados = []

                # Suporte para diferentes estruturas de XML
                for nota in (
                    root.findall(".//Nota")
                    or root.findall(".//NFe")
                    or root.findall(".//NFSE")
                ):
                    info = {}
                    for elem in nota.iter():
                        info[elem.tag] = elem.text
                    dados.append(info)

                if not dados:
                    return (
                        "Erro: Estrutura de XML não reconhecida. Verifique o arquivo."
                    )

                df = pd.DataFrame(dados)
                self.memoria.salvar("arquivo_carregado", df)
                return df
            except Exception as e:
                return f"Erro ao carregar arquivo XML: {e}"
        else:
            return "Formato de arquivo não suportado."

    def validar_arquivo(self):
        """
        Valida os dados do arquivo carregado na memória compartilhada.
        :return: Relatório de erros ou mensagem de sucesso.
        """
        df = self.memoria.obter("arquivo_carregado")
        if df is None or df.empty:
            return "Nenhum arquivo carregado para validação."

        erros = DataValidator.validar_dados(df)
        if erros:
            return "Erros encontrados na validação:\n" + "\n".join(erros)
        return "Arquivo validado com sucesso, sem erros encontrados."

    def gerar_resposta(self, pergunta):
        """
        Gera uma resposta com base nos dados carregados e na pergunta fornecida.
        :param pergunta: Pergunta em linguagem natural.
        :return: Resposta gerada ou mensagem de erro.
        """
        df = self.memoria.obter("arquivo_carregado")
        if df is None or df.empty:
            return "Nenhum dado disponível para gerar uma resposta."

        return self.gerar_resposta_llm(pergunta)

    def gerar_resposta_llm(self, pergunta):
        """
        Gera uma resposta com base na pergunta e nos dados carregados.
        :param pergunta: Pergunta em linguagem natural.
        :return: Resposta gerada.
        """
        df = self.memoria.obter("arquivo_carregado")
        if df is None or df.empty:
            return "Nenhum dado disponível para análise."

        # Integração com o módulo llm_utils
        return llm_resposta(pergunta, df)


# Exemplo de uso
if __name__ == "__main__":
    manager = AgentManager()
    print(manager.processar_entrada("notas_fiscais.csv", "arquivo"))
    print(manager.coordenar_modulos())
