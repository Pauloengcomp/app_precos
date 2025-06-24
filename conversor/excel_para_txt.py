import pandas as pd
import os

def converter_df_para_txt(df, caminho_destino):
    # Limpa os dados
    linhas = df.astype(str).applymap(lambda x: str(x).replace('\n', ' ').strip()).values.tolist()
    linhas_txt = ['|'.join(linha) for linha in linhas if any(c.strip() for c in linha)]

    with open(caminho_destino, 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas_txt))

    return caminho_destino