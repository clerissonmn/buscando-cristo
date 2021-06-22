from io import BytesIO

import pandas as pd
import streamlit as st
import requests

# ----[ Flags ]--------------------------------------------------------------------------- #

verbose = False

# ----[Funções ]-------------------------------------------------------------------------- #
@st.cache()
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

def aplica_filtro(df=None, programas=None, natureza=None, bairros=None, cidades=None,verbose=False):
    
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

    if len(bairros)>0:
        filtro_bairro = f"{bairros} in Bairro"
        df_filtrado = df_filtrado.query(filtro_bairro)

    # ----[Filtro: Cidades]---- #

    if not "Todas" in cidades:
        filtro_cidade = f"{cidades} in Cidade"
        df_filtrado = df_filtrado.query(filtro_cidade)

    # ----[Mostra df]---- #
    if verbose: print('Saindao da função. Tudo ok!')
    return df_filtrado.fillna('').sort_values(by='Programação')

# -------------[ Dados: Baixa os dados]------------- #

with st.spinner(text='Carregando a tabela'):
    df = get_csv_to_df(verbose=verbose)
bairros = [i for i in df.Bairro.dropna().unique()]
cidades = [i for i in df.Cidade.dropna().unique()]

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
    """)

# -------------[ STREAMLIT : Controles]------------- #

with user_input:

    # Controles
    with st.beta_expander('Filtrar'):
        cols = st.beta_columns(4)
        sb_mostrar  = cols[0].selectbox('Mostrar:', ['Missa','Adoração','Confissão'])
        sb_natureza = cols[1].selectbox('Tipo', ['Presencial','Transmitido'])
        ms_bairros  = cols[2].multiselect('Bairro:', bairros)
        sb_cidades  = cols[3].selectbox('Cidade:', ['Todas']+cidades)
    
    programas = [sb_mostrar]
    natureza  = [sb_natureza]
    bairros   = ms_bairros
    cidades   = [sb_cidades]

    texto = f"Horário das"

    # Missa, adoração ou confissões
    if sb_mostrar == "Missa":
        texto += ' missas'
    elif sb_mostrar == "Adoração":
        texto += ' adorações'
    elif sb_mostrar == "Confissão":
        texto += ' confissões'

    if sb_natureza == "Presencial":
        texto += ' presenciais'
        sep1, sep2 = [' |',', ']
    elif sb_natureza == "Transmitido":
        texto += ' transmitidas'
        sep1, sep2 = [' ','']

    if len(ms_bairros) == 0:
        #texto += ', em todos os bairros'
        texto += ' em'
        pass
    else:
        texto += ' em alguns bairros de'

    if sb_cidades == "Todas":
        texto += ' Belém e Ananindeua'
    elif sb_cidades == "Belém":
        texto += ' Belém'
    elif sb_cidades == "Ananindeua":        
        texto += ' Ananindeua'
    st.subheader(texto)

# -------------[ STREAMLIT : Dados]------------- #

    colunas = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    
    data = aplica_filtro(df=df, programas=programas, natureza=natureza, bairros=bairros, cidades=cidades, verbose=verbose)
    data['indice'] = data['Local']+sep1+data['Endereço']+sep2+data['Bairro']+sep1+data['Contato']+sep2

    data.set_index('indice', inplace=True)

    tabela = data[colunas]

# -------------[ STREAMLIT: Mostra a tabela ]------------- #
    st.table(tabela)

with author_credits:
    #st.header(f'Estatística')
    st.markdown("""
    "Pedi e vos será dado; buscai e achareis; batei e vos será aberto."**$_{(Mt\,7,7)}$**    
    """)