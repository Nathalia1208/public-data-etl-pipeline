from extract import extrair_municipios_ibge, extrair_csv_publico
from transform import transformar_municipios
from load import carregar_dados

def executar_pipeline():
    print("Inicio do  pipeline ETL")

    extrair_municipios_ibge()
    extrair_csv_publico()
    transformar_municipios()
    carregar_dados()

    print("Pipeline feitoo!")

if __name__ == "__main__":
    executar_pipeline()