import pandas as pd

def load_produtos_data():
    return pd.read_csv('data/produtos.csv')

def load_artistas_data():
    return pd.read_csv('data/artistas.csv')

def prepare_data(relatorio_df, artistas_df, produtos_df):
    # Extrair o código do artista
    relatorio_df['artista'] = relatorio_df['itemSku'].apply(lambda x: x.split('-')[-2])
    
    # Merge com artistas
    merged_df1 = relatorio_df.merge(artistas_df, how='left', left_on='artista', right_on='baseSku')
    
    # Merge com produtos
    merged_df2 = merged_df1.merge(produtos_df[['sku', 'name']], how='left', left_on='itemSku', right_on='sku')

    # Limpeza de nome
    merged_df2['name'] = merged_df2['name'].str.replace('(ESTAMPADA) Camiseta ', '', regex=False)

    return merged_df2

def aggregate_data(merged_df2):
    # Preparar a tabela agregada
    tabela_aggregada = (
        merged_df2.groupby(['itemSku', 'name', 'nameArtista'], as_index=False)
        .agg({
            'quantidadeVendida': 'sum',
            'lucroPorModelo': 'sum'
        })
        .rename(columns={
            'itemSku': 'SKU',
            'name': 'Nome Produto',
            'quantidadeVendida': 'Quantidade Vendida',
            'lucroPorModelo': 'Lucro Por Modelo'
        })
    )
    
    tabela_aggregada['Lucro Por Modelo R$'] = tabela_aggregada['Lucro Por Modelo'].apply(lambda x: f'R$ {x:,.2f}')
    return tabela_aggregada
