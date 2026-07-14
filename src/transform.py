import pandas as pd
import json
from pathlib import Path

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def transformar_municipios():
    caminho_json = RAW_PATH / "municipios_ibge.json"

    with open(caminho_json, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    df = pd.json_normalize(dados)

    print("Colunas encontradas no JSON:")
    print(df.columns)

    colunas_desejadas = {
        "id": "id_municipio",
        "nome": "municipio",
        "regiao-imediata.nome": "regiao_imediata",
        "regiao-imediata.regiao-intermediaria.nome": "regiao_intermediaria",
        "regiao-imediata.regiao-intermediaria.UF.nome": "uf",
        "regiao-imediata.regiao-intermediaria.UF.sigla": "sigla_uf",
        "regiao-imediata.regiao-intermediaria.UF.regiao.nome": "regiao"
    }

    df = df[list(colunas_desejadas.keys())]
    df = df.rename(columns=colunas_desejadas)

    caminho_saida = PROCESSED_PATH / "municipios_tratados.csv"
    df.to_csv(caminho_saida, index=False, encoding="utf-8")

    print("Transformação concluída com sucesso!")
    print(f"Total de municípios tratados: {len(df)}")

def transformar_populacao():

    caminho_csv = RAW_PATH / "populacao.csv"

    df = pd.read_csv(caminho_csv)

    print("\nColunas da base de população:")
    print(df.columns)

    colunas_desejadas = {
        "codigo_ibge": "id_municipio",
        "nome": "municipio",
        "capital": "capital",
        "codigo_uf": "codigo_uf",
        "siafi_id": "siafi_id",
        "ddd": "ddd",
        "fuso_horario": "fuso_horario"
    }

    df = df[list(colunas_desejadas.keys())]

    df = df.rename(columns=colunas_desejadas)

    caminho_saida = PROCESSED_PATH / "populacao_tratada.csv"

    df.to_csv(caminho_saida, index=False, encoding="utf-8")

    print("Transformação da população concluída!")
    print(f"Total de registros: {len(df)}")


if __name__ == "__main__":
    transformar_municipios()
    transformar_populacao()