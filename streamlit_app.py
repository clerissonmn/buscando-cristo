from io import BytesIO

import pandas as pd
import streamlit as st
import requests

# ----[ Flags ]--------------------------------------------------------------------------- #

verbose = False

# ----[Funções ]-------------------------------------------------------------------------- #

def get_csv_to_df(doc_key='1Behv9qOYb-1vfK4Mx8fUACmt6FCyLelaEdjQVEvuQmA', sheet_name='df', verbose=False):
    """
    Baixa o csv a partir do googlesheet
    """
    raw_link   = f'https://docs.google.com/spreadsheets/d/{doc_key}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    
    if verbose: print('Link:',raw_link)

    response = requests.get(raw_link)

    assert response.status_code == 200, 'Wrong status code'
    
    raw_csv = BytesIO(response.content)
    
    df = pd.read_csv(raw_csv)
    
    if verbose: st.write(df)

    return df

def aplica_filtro(df=None, programas=None, natureza=None, bairro=None, verbose=False):
    
    if verbose: print('Programas:', programas)
    if verbose: print('Natureza:',natureza)
    if verbose: print('Bairro:', bairro)
    if verbose: print('Bairros:', bairros)
    
    
    df_filtrado = df.copy()

    # ----[Filtro: Programa]---- #
    
    if len(programas)>0:
        filtro_programacao = f"{programas} in Programação"
        df_filtrado = df_filtrado.query(filtro_programacao)

    # ----[Filtro: Natureza]---- #

    if natureza:
        filtro_natureza = f"{natureza} in Natureza"
        df_filtrado = df_filtrado.query(filtro_natureza)

    # ----[Filtro: Bairro]---- #

    if not 'Todos' in bairro:
        filtro_bairro = f"{bairro} in Bairro"
        df_filtrado = df_filtrado.query(filtro_bairro)


    # ----[Mostra df]---- #
    if verbose: print('Saindao da função. Tudo ok!')
    return df_filtrado.fillna('').sort_values(by='Programação')

# -------------[ Dados: Baixa os dados]------------- #

df = get_csv_to_df(verbose=verbose)
bairros = [i for i in df.Bairro.dropna().unique()]

# -------------[ STREAMLIT: containers]------------- #

header = st.beta_container()
user_input = st.beta_container()
output_table = st.beta_container()
author_credits = st.beta_container()

# -------------[ STREAMLIT: header]------------- #

with header:
    st.title('Mapa de horários')
    st.markdown("""
    #### Importante! 
      - Confirmar os horários;
      - Necessidade de agendamento;
      - Necessidade de senha.

**Dica:** Se os `Filtros` não estiverem aparecendo, clique no ícone `>` no canto
superior esquerdo da tela.
    """)

# -------------[ STREAMLIT : Controles]------------- #

with user_input:
    st.sidebar.subheader(f'Filtros: ')

    st.sidebar.subheader(f'Mostrar: ')
    cb_confissao = st.sidebar.checkbox('Confissão')
    cb_missa = st.sidebar.checkbox('Missa', value=True)
    cb_adoracao = st.sidebar.checkbox('Adoração')

    programas = list()
    if cb_confissao:
        programas.append('Confissão')
    if cb_missa:
        programas.append('Missa')
    if cb_adoracao:
        programas.append('Adoração')


    st.sidebar.subheader(f'Ver: ')
    rb_natureza = st.sidebar.radio('',
                            ('Todos', 'Transmitido', 'Presencial'),
                            index=2)

    if rb_natureza == 'Transmitido':
        natureza = ['Transmitido']
    elif rb_natureza == 'Presencial':
        natureza = ['Presencial']
    else:
        natureza = None

    if rb_natureza == "Transmitido":
        bairro = ['Todos']
    else:
        st.sidebar.subheader(f'Bairros: ')
        cb_mostra_bairros = st.sidebar.checkbox('Escolher bairros')
        if cb_mostra_bairros:
            bairro = st.sidebar.multiselect(
                    '',
                    bairros,
                    bairros[0])
        else:
            bairro = ['Todos']


# -------------[ STREAMLIT : Dados]------------- #

colunas = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

data = aplica_filtro(df=df, programas=programas, natureza=natureza, bairro=bairro, verbose=verbose)
data['indice'] = data['Local']+' |'+data['Endereço']+', '+data['Bairro']+' | '+data['Contato']+'|'

data.set_index('indice', inplace=True)

tabela = data[colunas]

# --[ STREAMLIT: output ]---------------------- #

with output_table:
    
    st.table(tabela)

with author_credits:
    #st.header(f'Estatística')
    st.markdown("""
    "Pedi e vos será dado; buscai e achareis; batei e vos será aberto."**$_{(Mt\,7,7)}$**    
    """)