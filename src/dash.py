import pandas as pd
import streamlit as st
from dao import get_data_from_db
from pandas_utils import load_produtos_data, load_artistas_data, prepare_data, aggregate_data
from config import MIN_DATE

def render_dash():
    # Configuração do Streamlit
    st.sidebar.title("Filtros")

    start_date = st.sidebar.date_input(
        "Start date", 
        value=MIN_DATE, 
        min_value=MIN_DATE
    )

    end_date = st.sidebar.date_input(
        "End date", 
        value=MIN_DATE + pd.Timedelta(days=14), 
        min_value=MIN_DATE
    )

    # Carregar os dados
    produtos_df = load_produtos_data()
    artistas_df = load_artistas_data()
    relatorio_df = get_data_from_db(start_date, end_date)

    # Preparar os dados
    merged_df2 = prepare_data(relatorio_df, artistas_df, produtos_df)

    # Agregar os dados
    tabela_aggregada = aggregate_data(merged_df2)

    # Filtro de artista
    artista_selecionado = st.sidebar.selectbox("Selecione o Artista", ['Todos'] + artistas_df['name_artista'].unique().tolist())

    titulo = "Todos"
    if artista_selecionado != 'Todos':
        tabela_filtrada = tabela_aggregada[tabela_aggregada['name_artista'] == artista_selecionado]
        titulo = artista_selecionado
    else:
        tabela_filtrada = tabela_aggregada

    # Exibir dados no Streamlit
    tabela_display = tabela_filtrada.drop(columns=['Lucro Por Modelo'])

    lucro_total = tabela_filtrada['Lucro Por Modelo'].sum()
    quantidade_total = tabela_filtrada['Quantidade Vendida'].sum()

    st.title("Dashboard de Vendas de " + titulo)
    st.dataframe(tabela_display, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Peças Vendidas", f"{quantidade_total:,.0f} Unds.")

    with col2:
        st.metric("Lucro Total", f"R${lucro_total:,.2f}")

    st.markdown("""
        <style>
            .streamlit-expanderHeader {
                background-color: #f0f0f0;
            }
            table {
                width: 100%;
            }
            .stMainBlockContainer{
                max-width: none;
            }
        </style>
    """, unsafe_allow_html=True)

def log_out():
    log_out = st.sidebar.button("Sair")
        
    if log_out:
        st.session_state.logged_in = False
        st.rerun()

def login():
    st.title("Login")
    # Input para o nome de usuário
    username = st.text_input("Usuário")
    # Input para a senha (oculta)
    password = st.text_input("Senha", type="password")
    # Botão de login
    login_button = st.button("Entrar")

    # Checando se o login foi clicado
    if login_button:
        # Verificar as credenciais (Exemplo simples, substitua com suas credenciais reais)
        if username == "teste" and password == "teste":
            st.success("Login realizado com sucesso!")
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")