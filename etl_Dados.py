import pandas as pd
import re
import os

# -------------------- Configurações --------------------

excel_file = pd.ExcelFile('vagas_e_candidaturas.xlsx') 

#Acesso a aba Listagem de Vagas da planilha vagas_e_candidaturas.xlsx
df_vagas = excel_file.parse('Listagem de Vagas')
print("Dados da aba 'Listagem de Vagas':")
lista_de_colunas = df_vagas.columns.tolist()
print(lista_de_colunas)
print(df_vagas)

#Acesso as abas da planilha vagas_e_candidaturas.xlsx
candidaturas = {}
for aba_numero in ['1 - Cientista de Dados Sênior', '2 - Engenheiro de Software - PL', '3 - Cientista de Dados - Júnior', '4 - Engenheiro de Software - SR']:
    try:
        df_candidaturas = excel_file.parse(aba_numero)
        candidaturas[f'Vaga_{aba_numero}'] = df_candidaturas
        
        #lista_de_colunas = df_candidaturas.columns.tolist()
        #print(lista_de_colunas)

        #Ver o tipo das colunas trabalhadas
        print("Tipo das Colunas:")
        print(df_candidaturas.dtypes)

        print(f"\nDados da aba '{aba_numero}' (Candidaturas Vaga {aba_numero}):")
        print(df_candidaturas)

    except ValueError:
        print(f"\nAba '{aba_numero}' não encontrada.")

# -------------------- Formatações --------------------

# Função para formatar telefone
def formatar_telefone(telefone):
    if pd.isna(telefone):
        return ''
    
    telefone = str(telefone)
    telefone = re.sub(r'\D', '', telefone)  #substituições de substrings em uma string com base em um padrão de expressão ( Remove caracteres não numérico)

    if len(telefone) == 11:  

        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}" #formatando o número (99) 99999-9999

    elif len(telefone) == 10: 

        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}" #Essa parte foi add para tratar um possivel erro de esquecer de colocar o 9 na frente

    return telefone


# Função para formatar e-mail
def formatar_email(email):
    if pd.isna(email):  #testa se um valor é NaN
        return ''

    return email.strip()


# Função para formatar LinkedIn
def formatar_linkedin(linkedin):
    if pd.isna(linkedin):
        return 'missing@inhire.com.br'

    return linkedin.strip()

#função para transformar as tags em lista
def formatar_tags(tag):
    if pd.isna(tag):
        return []
    return [item.strip() for item in tag.split(',')]

#função para formatar cidade e estado
def formatar_cidade_estado(cidade_estado):

    cidade_estado = str(cidade_estado)
    if pd.isna(cidade_estado):
        return ''
    
    return cidade_estado.replace('-', '').strip()

 #função para formatar colunas para datetime com tratamento de erros para NaT
def formatar_datetime(df):

    for col in df.columns:
        
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except:
            pass #duvida: e a coluna não puder ser convertida para datetime, mantém como está

    return df

#aplicar as funções de formatação
df_vagas['Telefone'] = df_candidaturas['Telefone'].apply(formatar_telefone)
df_vagas['email'] = df_candidaturas['email'].apply(formatar_email)
df_vagas['Linkedin'] = df_candidaturas['Linkedin'].apply(formatar_linkedin)
df_vagas['tag'] = df_candidaturas['tags'].apply(formatar_tags)
df_vagas['Localização'] = df_candidaturas['Localização'].apply(formatar_cidade_estado)  

# -------------------- Limpeza e Otimização --------------------

#removendo as linhas onde tanto 'email' quanto 'Linkedin' são NaN
df = df_candidaturas.dropna(subset=['email', 'Linkedin'], how='all') 

#função para gerar e-mail
def gerar_email(first_name, second_name):
    if pd.isna(first_name) or pd.isna(second_name):
        return ''

    return f"{first_name.lower()}.{second_name.lower()}@inhire.com.br"




# -------------------- Função para Extrair e Transformar --------------------
"""
def ler_e_padronizar_planilha(caminho_arquivo):
    try:
        # Tenta ler a planilha (pode ser .xlsx ou .csv)
        if caminho_arquivo.endswith('.xlsx'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            df = pd.read_csv(caminho_arquivo)
        else:
            print(f"Arquivo não suportado: {caminho_arquivo}")
            return None

        print(f"Processando: {caminho_arquivo}")
    
        # Padronização dos nomes das colunas (case insensitive e removendo espaços)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Cria um dicionário para mapear as colunas encontradas para os nomes esperados
        mapping = {}
        for coluna_esperada in candidaturas:
            coluna_formatada = coluna_esperada.lower().replace(' ', '_')
            for coluna_existente in df.columns:
                if coluna_formatada in coluna_existente: # Permite variações nos nomes
                    mapping[coluna_existente] = coluna_formatada
                    break # Assume que encontrou a melhor correspondência

        # Renomeia as colunas
        df = df.rename(columns=mapping)

        # Seleciona apenas as colunas que foram mapeadas para as colunas esperadas
        df = df[list(mapping.values())]

        # Garante que todas as colunas esperadas estejam presentes (com NaN se não houver)
        for coluna_formatada in [col.lower().replace(' ', '_') for col in candidaturas]:
            if coluna_formatada not in df.columns:
                df[coluna_formatada] = pd.NA

        return df[ [col.lower().replace(' ', '_') for col in candidaturas] ] # Retorna na ordem esperada

    except Exception as e:
        print(f"Erro ao ler o arquivo {caminho_arquivo}: {e}")
        return None

# -------------------- Função para Carregar --------------------
def consolidar_dados(lista_de_dataframes, arquivo_destino):
    if not lista_de_dataframes:
        print("Nenhum dado para consolidar.")
        return

    df_consolidado = pd.concat(lista_de_dataframes, ignore_index=True)

    try:
        df_consolidado.to_excel(arquivo_destino, index=False)
        print(f"Dados consolidados e salvos em: {arquivo_destino}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo consolidado: {e}")

# -------------------- Fluxo Principal do ETL --------------------
if __name__ == "_main_":
    arquivos_encontrados = [os.path.join(pasta_origem, f) for f in os.listdir(pasta_origem) if f.endswith(('.xlsx', '.csv'))]
    dataframes = []

    for arquivo in arquivos_encontrados:
        df = ler_e_padronizar_planilha(arquivo)
        if df is not None:
            dataframes.append(df)

    consolidar_dados(dataframes, arquivo_destino)
"""