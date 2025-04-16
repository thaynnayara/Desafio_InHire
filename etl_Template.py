import pandas as pd
import os

excel_file = pd.ExcelFile('inhire_template.xlsx') 

candidaturas = {}
for abas in ['jobs', 'applications', 'types']:
    try:
        df_template = excel_file.parse(abas)
        candidaturas[f'Vaga_{abas}'] = df_template
        print(f"\nDados da aba '{abas}' (Candidaturas Vaga {abas}):")
        print(df_template)
    except ValueError:
        print(f"\nAba '{abas}' não encontrada.")