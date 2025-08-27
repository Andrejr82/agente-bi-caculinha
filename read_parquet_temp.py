import pandas as pd
import os

parquet_file = os.path.join("U:\\Meu Drive\\Caçula\\Langchain\\Agent_BI\\data\\parquet_cleaned", "admatao.parquet")

try:
    df = pd.read_parquet(parquet_file)
    print(df.head().to_string())
except Exception as e:
    print(f"Erro ao ler o arquivo parquet: {e}")