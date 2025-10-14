# visualization.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


class Visualization:
    """
    Classe responsável por gerar gráficos e visualizações interativas.
    """

    @staticmethod
    def gerar_grafico_barras(df: pd.DataFrame, x: str, y: str):
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x=x, y=y)
        plt.title("Gráfico de Barras")
        plt.show()

    @staticmethod
    def gerar_grafico_linhas(df: pd.DataFrame, x: str, y: str):
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x=x, y=y)
        plt.title("Gráfico de Linhas")
        plt.show()

    @staticmethod
    def gerar_grafico_interativo(df: pd.DataFrame, x: str, y: str):
        fig = px.bar(df, x=x, y=y, title="Gráfico Interativo de Barras")
        fig.show()
