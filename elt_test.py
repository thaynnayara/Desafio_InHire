import pandas as pd
from openpyxl import load_workbook
import os

# Planilha de origem
arquivo_origem = 'vagas_e_candidaturas.xlsx'
df_origem = pd.read_excel(arquivo_origem, sheet_name='nome_da_aba_origem')

# Planilha de destino (template)
arquivo_destino = 'inhire_template.xlsx'
workbook_destino = load_workbook(arquivo_destino)


#excel_file = pd.ExcelFile('vagas_e_candidaturas.xlsx') 

#df_vagas = excel_file.parse('Listagem de Vagas')
#print("Dados da aba 'Listagem de Vagas':")
#print(df_vagas)

candidaturas = {}
for aba_numero in ['1 - Cientista de Dados Sênior', '2 - Engenheiro de Software - PL', '3 - Cientista de Dados - Júnior', '4 - Engenheiro de Software']:
    try:
        df_candidaturas = df_origem.parse(aba_numero)
        candidaturas[f'Vaga_{aba_numero}'] = df_candidaturas
        print(f"\nDados da aba '{aba_numero}' (Candidaturas Vaga {aba_numero}):")
        print(df_candidaturas)
    except ValueError:
        print(f"\nAba '{aba_numero}' não encontrada.")

sheet_destino = workbook_destino[candidaturas] # Ou selecione uma aba específica: workbook_destino['Nome da Aba']

# Exemplo: Extrair colunas específicas

colunas_desejadas = ['Coluna A da Origem', 'Coluna C da Origem', 'Outra Coluna']
df_filtrado = df_origem[colunas_desejadas].copy() # Use .copy() para evitar warnings

# Exemplo: Filtrar linhas com base em alguma condição
condicao = df_origem['Coluna B da Origem'] > 10
df_filtrado = df_origem[condicao][colunas_desejadas].copy()

# Exemplo: Renomear colunas para corresponder ao template (opcional)
mapeamento_colunas = {'Coluna A da Origem': 'Coluna 1 no Destino',
                       'Coluna C da Origem': 'Coluna 2 no Destino',
                       'Outra Coluna': 'Coluna 3 no Destino'}
df_filtrado.rename(columns=mapeamento_colunas, inplace=True)