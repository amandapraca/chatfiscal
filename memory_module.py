# memory_module.py

import threading


class MemoriaCompartilhada:
    """
    Classe para gerenciar memória compartilhada entre os módulos.
    """

    def __init__(self):
        self.dados = {}
        self.lock = threading.Lock()

    def salvar(self, chave, valor):
        """
        Salva um valor na memória compartilhada.
        :param chave: Chave identificadora do dado.
        :param valor: Valor a ser armazenado.
        """
        with self.lock:
            self.dados[chave] = valor

    def obter(self, chave):
        """
        Obtém um valor da memória compartilhada.
        :param chave: Chave identificadora do dado.
        :return: Valor armazenado ou None se a chave não existir.
        """
        with self.lock:
            return self.dados.get(chave)


class MemoriaDedicada:
    """
    Classe para gerenciar memória dedicada para cada módulo.
    """

    def __init__(self):
        self.dados = {}

    def salvar(self, chave, valor):
        """
        Salva um valor na memória dedicada.
        :param chave: Chave identificadora do dado.
        :param valor: Valor a ser armazenado.
        """
        self.dados[chave] = valor

    def obter(self, chave):
        """
        Obtém um valor da memória dedicada.
        :param chave: Chave identificadora do dado.
        :return: Valor armazenado ou None se a chave não existir.
        """
        return self.dados.get(chave)


# Exemplo de uso
if __name__ == "__main__":
    # Memória Compartilhada
    memoria_compartilhada = MemoriaCompartilhada()
    memoria_compartilhada.salvar("arquivo_carregado", {"nome": "notas_fiscais.csv"})
    print("Memória Compartilhada:", memoria_compartilhada.obter("arquivo_carregado"))

    # Memória Dedicada
    memoria_dedicada = MemoriaDedicada()
    memoria_dedicada.salvar("resumo", "Resumo dos dados gerado.")
    print("Memória Dedicada:", memoria_dedicada.obter("resumo"))
