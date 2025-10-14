# erp_integration.py


class ERPIntegration:
    """
    Classe responsável por integrar o sistema com ERPs (Domínio, Alterdata, Protheus).
    """

    @staticmethod
    def enviar_dados_para_erp(dados, erp):
        """
        Envia dados para o ERP especificado.
        :param dados: Dados a serem enviados.
        :param erp: Nome do ERP (e.g., "Domínio", "Alterdata", "Protheus").
        """
        if erp == "Domínio":
            # Implementar integração com Domínio
            pass
        elif erp == "Alterdata":
            # Implementar integração com Alterdata
            pass
        elif erp == "Protheus":
            # Implementar integração com Protheus
            pass
        else:
            raise ValueError("ERP não suportado.")

    @staticmethod
    def receber_dados_do_erp(erp):
        """
        Recebe dados do ERP especificado.
        :param erp: Nome do ERP (e.g., "Domínio", "Alterdata", "Protheus").
        :return: Dados recebidos.
        """
        if erp == "Domínio":
            # Implementar integração com Domínio
            pass
        elif erp == "Alterdata":
            # Implementar integração com Alterdata
            pass
        elif erp == "Protheus":
            # Implementar integração com Protheus
            pass
        else:
            raise ValueError("ERP não suportado.")
