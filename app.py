from io import BytesIO

import pandas as pd
import streamlit as st
import requests


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


df = get_csv_to_df()

# -------------[ STREAMLIT : Controles]------------- #
st.subheader(f'Mostrar: ')
programas = list()
if st.checkbox('Confissão'):
    programas.append('Confissão')
if st.checkbox('Missa', value=True):
    programas.append('Missa')
if st.checkbox('Adoração'):
    programas.append('Adoração')


st.subheader(f'Apenas: ')
rb_natureza = st.radio('',
                        ('Todos', 'Transmitido', 'Presencial'),
                        index=2)

if rb_natureza == 'Transmitido':
    natureza = ['Transmitido']
elif rb_natureza == 'Presencial':
    natureza = ['Presencial']
else:
    natureza = None

bairros = [i for i in df.Bairro.dropna().unique()]
if rb_natureza == "Transmitido":
    bairro = ['Todos']
else:
    st.subheader(f'Bairros: ')
    if st.checkbox('Escolher bairros'):
        bairro = st.multiselect(
                '',
                bairros,
                bairros[0])
    else:
        bairro = ['Todos']


# -------------[ STREAMLIT : Dados]------------- #

colunas = ['Local','Bairro', 'Contato', 
           'Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

data = aplica_filtro(df=df, programas=programas, natureza=natureza, bairro=bairro, verbose=True)

# -------------[ STREAMLIT : View]------------- #
st.title('Mapa de horários')

st.write(data[colunas])
