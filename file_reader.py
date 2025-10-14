# file_reader.py

import pandas as pd
import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image


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

            # Processar NFSe
            for nota in root.findall(".//nf"):
                info = {
                    "numero_nfse": nota.findtext("numero_nfse"),
                    "data_nfse": nota.findtext("data_nfse"),
                    "valor_total": nota.findtext("valor_total"),
                    "observacao": nota.findtext("observacao"),
                }
                dados.append(info)

            # Processar NFe (se aplicável)
            for nota in root.findall(".//NFe"):
                info = {}
                for elem in nota.iter():
                    info[elem.tag] = elem.text
                dados.append(info)

            # Processar outras tags genéricas
            for nota in root.findall(".//NotaFiscal"):
                info = {}
                for elem in nota.iter():
                    info[elem.tag] = elem.text
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
