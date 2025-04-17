import pandas as pd
from openpyxl import load_workbook
import re
import os

# --------- Configurações --------

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

#Tipo de dados de cada coluna
# df_vagas['Código'] = df_vagas['Código'].astype(str) 

#------------- Formatações -------------

#Função para formatar telefone
def formatar_telefone(telefone):
    
    if pd.isna(telefone) or str(telefone).strip() == '' or len(str(telefone).strip()) <= 1:

        return '' #substituições de substrings em uma string com base em um padrão de expressão ( Remove caracteres não numérico)

    if len(telefone) == 11:  

        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}" #formatando o número (00)00000-0000

    elif len(telefone) == 10: 

        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}" #Essa parte foi add para tratar um possivel erro de esquecer de colocar o 9 na frente

    return telefone

#função para gerar e-mail, visto que o email seguia um padrão de primeiro e segundo nome...
def gerar_email(nome_completo):

    if pd.isna(nome_completo) or nome_completo.strip() == '':
        return 'Nome está ausente!'
    
    #dividindo o nome
    partes = nome_completo.split()
    
    #se existirem pega o primeiro nome
    primeiro_nome = partes[0] if len(partes) > 0 else ''
    segundo_nome = partes[1] if len(partes) > 1 else ''
    
    #gerando o e-mail depois das condições acimas corresponderem
    return f"{primeiro_nome.lower()}{segundo_nome.lower()}@desafiodados001.com"
    


#Função para formatar LinkedIn, foi usado 'https://www.linkedin.com/in/missing' pois pode acontecer que na hora de passar os dados para o template gere erro
def formatar_linkedin(linkedin):
    
    if pd.isnull(linkedin):
        return 'https://www.linkedin.com/in/missing'
    return linkedin.strip()

#função para transformar as tags em lista, como foi especificado pelo template
def formatar_tags(tag: str):
    if pd.isna(tag):
        return ''
    return [item.strip() for item in tag.split(',')]

#função para formatar cidade e estado, nesse caso foi retirado '-' dos dados que estavam sem a cidade e estado e fica mais fácil para separar depois
def formatar_cidade_estado(cidade_estado):

    cidade_estado = str(cidade_estado)
    if pd.isna(cidade_estado):
        return ''
    
    return cidade_estado.replace('-', '').strip()

 #função para formatar colunas para datetime com tratamento de erros para NaT - há outras formas de fazer
def formatar_datetime(df):

    for col in df.columns:
        
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except:
            pass #duvida:se a coluna não puder ser convertida para datetime, mantém como está

    return df

#--------- aplicar as funções de formatação ---------------

df_candidaturas['Telefone'] = df_candidaturas['Telefone'].apply(formatar_telefone)
print(df_candidaturas[['Telefone']].head())

df_candidaturas['email'] = df_candidaturas['Nome Candidato'].apply(gerar_email)
print(df_candidaturas[['email']].head())

df_candidaturas['Linkedin'] = df_candidaturas['Linkedin'].apply(formatar_linkedin)
print(df_candidaturas[['Linkedin']].median)

df_candidaturas['tag'] = df_candidaturas['tags'].apply(formatar_tags)
print(df_candidaturas[['tag']].head())

df_candidaturas['Localização'] = df_candidaturas['Localização'].apply(formatar_cidade_estado)  
print(df_candidaturas[['Localização']].head())

#----------- Otimização -----------

#Explicação: quando o candidato não colocou nenhuma das informações ele não é levado para o banco de talentos, como o template \
# isso pode ser modificado, pois foi uma interpretação minha

#removendo as linhas onde tanto 'email' quanto 'Linkedin' são NaN
df = df_candidaturas.dropna(subset=['email', 'Linkedin'], how='all') 
    

#Salvar o DataFrame com os dados gerados em um novo arquivo, usado por mim para ver o proguesso do código
df.to_excel('mudanças.xlsx', index=False)

#---------- Tratando dados --------------

# def tratar_cidade_estado(cidade_e_estado):

# Não vi nescessário a utilização desse codigo abaixo ainda, foi um pensamento que tive mas resolvi de outra forma

#      #dividindo o nome
#     partes = cidade_e_estado.split()
    
#     #se existirem pega o primeiro nome
#     cidade = partes[0] if len(partes) > 0 else ''
#     print(cidade)
#     estado = partes[1] if len(partes) > 1 else ''

#     return f"{cidade} {estado}"


#---- código das profições ----

#estou associando duas colunas juntas
codigos = df_vagas.groupby('Cargo')[str('Código')].agg(list).reset_index()
print(str(codigos))

#Carregar para uma planilha modelo que no caso do desafio é 'inhire_template.xlsx'
template = 'inhire_template.xlsx'

#Utilização do try para lidar com possivéis falhas evitando a interrupção abrupta
try:
    workbook_modelo = load_workbook(template)
except FileNotFoundError:
    print(f"Erro: Arquivo modelo '{template}' não encontrado.")
    exit()

try:

    df_cientistaSr = pd.read_excel('vagas_e_candidaturas.xlsx', sheet_name='1 - Cientista de Dados Sênior')
    df_engSofPl = pd.read_excel('vagas_e_candidaturas.xlsx', sheet_name='2 - Engenheiro de Software - PL')
    df_cientistaJr = pd.read_excel('vagas_e_candidaturas.xlsx', sheet_name='3 - Cientista de Dados - Júnior')
    df_engSoftSr = pd.read_excel('vagas_e_candidaturas.xlsx', sheet_name='4 - Engenheiro de Software - SR')
    df_jobs = pd.read_excel('inhire_template.xlsx', sheet_name='jobs')
    df_applications = pd.read_excel('inhire_template.xlsx', sheet_name='applications')


#tratamento de erro na busca do arquivo e mostra onde houve o erro, no caso a aba
except FileNotFoundError:
    print("Erro: Arquivo não encontrado.")
    exit()
except KeyError as erro:
    print(f"Erro: Aba '{erro}' não encontrada.")
    exit()

#s as colunas tiverem nomes diferentes nas abas
df_code = pd.merge(df_vagas, df_jobs, left_on='Código', right_on='code')

#coleta de colunas de forma direta e pegar com o .copy()
aba_jobs_template = 'jobs'
colunas_jobs_template = ['Cargo', 'Escritório', '']

#preciso completar o código enfrentei muitos problemas ao longo de seu desenvolvimento, \
#pórem digo que aprendi muita coisa me desafiando com esse desafio da InHire \
#pretendo dar sequência nele assim que possível.

