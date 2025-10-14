# test_file_reader.py

from file_reader import FileReader
import os


def test_carregar_csv():
    print("Testando carregamento de CSV...")
    caminho = os.path.abspath(os.path.join("data", "exemplo.csv"))
    print("Caminho absoluto do CSV:", caminho)
    if not os.path.exists(caminho):
        print("Arquivo CSV não encontrado no caminho especificado.")
        return
    try:
        df = FileReader.carregar_csv(caminho)
        print("CSV carregado com sucesso:")
        print(df.head())
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")


def test_carregar_xml():
    print("Testando carregamento de XML...")
    caminho = os.path.abspath(os.path.join("data", "exemplo.xml"))
    print("Caminho absoluto do XML:", caminho)
    if not os.path.exists(caminho):
        print("Arquivo XML não encontrado no caminho especificado.")
        return
    try:
        df = FileReader.carregar_xml(caminho)
        print("XML carregado com sucesso:")
        print(df.head())
    except Exception as e:
        print(f"Erro ao carregar XML: {e}")


if __name__ == "__main__":
    print("Diretório atual:", os.getcwd())
    test_carregar_csv()
    test_carregar_xml()
