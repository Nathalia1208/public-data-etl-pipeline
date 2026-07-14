import requests
import json
import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw")
RAW_PATH.mkdir(parents=True, exist_ok=True)


def extrair_municipios_ibge():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    resposta = requests.get(url)
    resposta.raise_for_status()

    dados = resposta.json()

    caminho_arquivo = RAW_PATH / "municipios_ibge.json"

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    print("Dados do IBGE salvos com sucesso!")


def extrair_csv_publico():
    url_csv = "https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv"

    df = pd.read_csv(url_csv)

    caminho_arquivo = RAW_PATH / "dados_publicos_exemplo.csv"

    df.to_csv(caminho_arquivo, index=False, encoding="utf-8")

    print("CSV público salvo com sucesso!")

def extrair_populacao():
    url = "https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/main/csv/municipios.csv"

    df = pd.read_csv(url)

    caminho_arquivo = RAW_PATH / "populacao.csv"

    df.to_csv(caminho_arquivo, index=False, encoding="utf-8")

    print("Dados de população salvos com sucesso!")


if __name__ == "__main__":
    extrair_municipios_ibge()
    extrair_csv_publico()
    extrair_populacao()
