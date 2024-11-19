import pandas as pd
import streamlit as st
from dao import get_data

pd.set_option('display.max_colwidth', None)

st.sidebar.title("Filtros")
start_date = st.sidebar.date_input("Start date", value=pd.to_datetime('2024-01-01'))
end_date = st.sidebar.date_input("End date", value=pd.to_datetime('2024-12-31'))

# Carregar os dados
produtos_df = pd.read_csv('produtos.csv')  # Substitua pelo caminho correto
relatorio_df = get_data(start_date, end_date)  # Substitua pelo caminho correto
artistas_df = pd.read_csv('artistas.csv')  # Substitua pelo caminho correto

# Extrair o código do artista da penúltima seção do item_sku
relatorio_df['artista'] = relatorio_df['item_sku'].apply(lambda x: x.split('-')[-2])
merged_df1 = relatorio_df.merge(artistas_df, how='left', left_on='artista', right_on='base_sku')

# Realizar o merge com base no SKU completo do relatorio e produtos
merged_df2 = merged_df1.merge(produtos_df[['sku', 'name']], how='left', left_on='item_sku', right_on='sku')

# Retirando o prefixo (ESTAMPADA) Camiseta 
merged_df2['name'] = merged_df2['name'].str.replace('(ESTAMPADA) Camiseta ', '', regex=False)

# Preparar os dados para o dashboard
tabela_aggregada = (
    merged_df2.groupby(['item_sku', 'name', 'name_artista'], as_index=False)
    .agg({
        'quantidade_vendida': 'sum',
        'lucro_por_modelo': 'sum'
    })
    .rename(columns={
        'item_sku': 'SKU',
        'name': 'Nome Produto',
        'quantidade_vendida': 'Quantidade Vendida',
        'lucro_por_modelo': 'Lucro Por Modelo'
    })
)

tabela_aggregada['Lucro Por Modelo R$'] = tabela_aggregada['Lucro Por Modelo'].apply(lambda x: f'R$ {x:,.2f}')

# Configuração do Streamlit
artista_selecionado = st.sidebar.selectbox("Selecione o Artista", ['Todos'] + artistas_df['name_artista'].unique().tolist())


titulo = "Todos"
if artista_selecionado != 'Todos':
    tabela_filtrada = tabela_aggregada[tabela_aggregada['name_artista'] == artista_selecionado]
    # Titulo dinamico
    titulo = artista_selecionado
else:
    tabela_filtrada = tabela_aggregada

# Fazendo uma tabela que mostra somente alguns dados
tabela_display = tabela_filtrada.drop(columns=['Lucro Por Modelo'])

# Soma total do lucro filtrado por artista
lucro_total = tabela_filtrada['Lucro Por Modelo'].sum()

st.title("Dashboard de Vendas de " + titulo)

st.dataframe(tabela_display, use_container_width=True) 

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