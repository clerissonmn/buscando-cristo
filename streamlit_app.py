from io import BytesIO

import pandas as pd
import streamlit as st
import requests

from funcoes.email import envia_email

import os

# ----[ Flags ]--------------------------------------------------------------------------- #

verbose = False

# ----[Funções ]-------------------------------------------------------------------------- #
#@st.cache()
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

def aplica_filtro(df=None, programas=None, natureza=None, bairros=None, cidades=None,verbose=False, local=None):
    
    if verbose: print('Programas:', programas)
    if verbose: print('Natureza:',natureza)
    if verbose: print('Bairros:', bairros)
    if verbose: print('Locais', local)
    
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

    # ----[Filtro: Local]---- #
    if not "Tudo" in local:
        filtro_local = f"{local} in Local"
        df_filtrado = df_filtrado.query(filtro_local)

    # ----[Mostra df]---- #
    if verbose: print('Saindao da função. Tudo ok!')
    return df_filtrado.fillna('').sort_values(by='Programação')

# -------------[ Dados: Baixa os dados]------------- #

with st.spinner(text='Carregando a tabela'):
    df = get_csv_to_df(verbose=verbose)

bairros = df.Bairro.sort_values().dropna().unique().tolist()
cidades = df.Cidade.sort_values().dropna().unique().tolist()
igrejas = df.Local.sort_values().dropna().unique().tolist()

# -------------[ STREAMLIT: containers]------------- #

header          = st.beta_container()
area_principal  = st.beta_container()
sobre_projeto   = st.beta_container()
form_envio      = st.beta_container()

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


with area_principal:

    # Controles
    #with st.beta_expander('Filtrar'):
    cols = st.beta_columns(4)
    sb_mostrar  = cols[0].selectbox('Mostrar:', ['Missa','Adoração','Confissão'])
    sb_natureza = cols[1].selectbox('Tipo', ['Presencial','Transmitido'])
    ms_bairros  = cols[2].multiselect('Bairro:', bairros)
    sb_cidades  = cols[3].selectbox('Município:', ['Todas']+cidades)
    
    #with st.beta_expander('Procurar por local'):
    sb_igrejas = st.selectbox('Locais: ',['Tudo']+igrejas, )

    programas = [sb_mostrar]
    natureza  = [sb_natureza]
    bairros   = ms_bairros
    cidades   = [sb_cidades]
    locais    = [sb_igrejas]

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


# -------------[ STREAMLIT : Dados]------------- #

    colunas = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    
    data = aplica_filtro(df=df, 
                         programas=programas, 
                         natureza=natureza, 
                         bairros=bairros, 
                         cidades=cidades,
                         local=locais,
                         verbose=verbose)

    data['indice'] = data['Local']+sep1+data['Endereço']+sep2+data['Bairro']+sep1+data['Contato']+sep2

    data.set_index('indice', inplace=True)

# -------------[ STREAMLIT: Mostra a tabela ]------------- #
    st.subheader(texto)
    tabela = data[colunas]
    st.table(tabela)


with sobre_projeto:
    st.header(f'Sobre o projeto')
    st.markdown(f""" Esta é uma iniciativa independente, ou seja, **não vinculado** à nenhuma
paróquia ou igreja em particular e conta com trabalho exclusivamente volutário.
As informações são obtidas mediante a coleta dos dados pelos próprios
mantenedores do App ou enviadas a eles por irmãos em Cristo.""")
    #st.markdown("""
    #"Pedi e vos será dado; buscai e achareis; batei e vos será aberto."**$_{(Mt\,7,7)}$**    
    #""")


with form_envio:
    st.subheader('Você também é muito bem-vindo a ajudar!!!')
    st.markdown(""" Você é convidado a nos ajudar a manter as informações o mais
confiável possível. Faça da forma que puder, por exemplo, você pode:
- Enviar horários de novos locais;
- Corrigir ou acrescentar os contatos;
- Corrigir ou completar os endereços dos locais;
- Adicionar observações para determinados horários. Por exemplo, se são missas
mais rápidas ou se precisa de agendamento, etc.

Use o formulário abaixo.
""")
    acao = st.radio('',['Quero enviar um novo', 'Quero enviar uma correção'])
    
    with st.form('Envio',clear_on_submit=True):
        #st.write("Preencha o formulário com os dados da paróquia, igreja, capela, etc.")
        if 'novo' in acao:
            st.subheader('Dados do local')
            cols = st.beta_columns(3)
            frm_programacao = cols[0].selectbox("Programação",["Missa e Confissão", 'Missa', 'Adoração', 'Confissão'])
            frm_nome        = cols[1].text_input(label='Nome')
            frm_endereco    = cols[2].text_input(label='Endereço')
            frm_contato     = cols[0].text_input(label='Contato')
            frm_bairro      = cols[1].text_input(label='Bairro')
            frm_municipio   = cols[2].text_input(label='Município')

            txt_dinamico = 'Horários'
            assunto = "Novo"
            lbl_horario = 'Horários:'
            texto = f"""
            Nome: {frm_nome}<br>
            Endereço: {frm_endereco}<br>
            Contato: {frm_contato}<br>
            Tipo: {frm_programacao}<br>
            Bairro: {frm_bairro}<br>
            Municipio: {frm_municipio}<br>
            Horários:"""
        elif 'correção' in acao:
            txt_dinamico = 'Qual a correção'
            assunto = 'Correção'
            texto='Correção: '
            lbl_horario = ''
        st.subheader(f'{txt_dinamico}')
        if txt_dinamico == 'Horários':
            st.markdown("""**Dica:** Escreva da forma mais confortável pra você mas coloque, também, as observações.

**Exemplos:**

    Missas:
    seg-sex 7h, 10h (cura), 12h
    ter 13h (rápida)
    qui 20h (agendamento pelo whatsapp)

    Confissão:
    seg 9 às 12h (mediante agendamento)
        """)
        frm_horarios = st.text_area(label=f'{lbl_horario}')
        
        enviado = st.form_submit_button("Enviar")
        if enviado:
            
            validacao = [
            frm_nome != "",
            frm_endereco != "",
            frm_contato != "",
            frm_bairro != "",
            frm_municipio != "",
            frm_horarios != ""]

            if all(validacao):
                
                destinatario = 'clerisson.mn@gmail.com'
                remetente = os.environ['var02']
                senha = os.environ['var01']
                
                mensagem = texto + f'{frm_horarios}'
                try:
                    envia_email(destinatario=destinatario,
                                remetente=remetente,
                                senha=senha,
                                mensagem=mensagem,
                                assunto=assunto)
                except:
                    st.error("Houve algum problema com o envio.")
                finally:
                    st.success('Enviado com sucesso, obrigado pela sua ajuda!')
                    st.balloons()
            else:
                st.error('Uma ou mais respostas parecem estar em branco. Você digitou todas as informações?')
