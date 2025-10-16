# file_reader.py

import pandas as pd
import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image
import logging


class FileReader:
    """
    Classe responsável por carregar e processar arquivos (CSV, XML, PDF).
    """

    @staticmethod
    def carregar_csv(arquivo):
        try:
            return pd.read_csv(arquivo, encoding="latin1", sep=None, engine="python")
        except Exception as e:
            raise ValueError(f"Erro ao carregar arquivo CSV: {e}")

    @staticmethod
    def carregar_xml(arquivo):
        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
            dados = []

            # Tentar diferentes estruturas de XML
            estruturas = [
                ".//nf",  # Para seu XML atual
                ".//NFe",  # Para NFe padrão
                ".//NotaFiscal",  # Para outras notas
                ".//NFSe",  # Para NFSe
                ".//Nota",  # Para estrutura genérica
            ]

            for estrutura in estruturas:
                notas = root.findall(estrutura)
                if notas:
                    for nota in notas:
                        info = {}
                        # Coletar todos os elementos filhos
                        for elem in nota.iter():
                            if elem.text and elem.text.strip():
                                info[elem.tag] = elem.text.strip()
                        # Também coletar atributos se existirem
                        for key, value in nota.attrib.items():
                            info[key] = value

                        if info:  # Só adicionar se tiver dados
                            dados.append(info)

                    break  # Para na primeira estrutura que encontrar

            if not dados:
                # Se não encontrou nenhuma estrutura conhecida, tentar extrair tudo
                logging.warning(
                    "Estrutura não reconhecida, extraindo todos os elementos"
                )
                for elem in root.iter():
                    if elem.text and elem.text.strip():
                        info = {elem.tag: elem.text.strip()}
                        dados.append(info)

            return pd.DataFrame(dados)

        except Exception as e:
            raise ValueError(f"Erro ao carregar arquivo XML: {e}")

    @staticmethod
    def carregar_pdf(arquivo):
        try:
            reader = PdfReader(arquivo)
            texto = ""
            for page in reader.pages:
                texto += page.extract_text()
            return texto
        except Exception as e:
            raise ValueError(f"Erro ao carregar arquivo PDF: {e}")

    @staticmethod
    def carregar_imagem_com_ocr(arquivo):
        try:
            imagem = Image.open(arquivo)
            texto = pytesseract.image_to_string(imagem, lang="por")
            return texto
        except Exception as e:
            raise ValueError(f"Erro ao processar imagem com OCR: {e}")
