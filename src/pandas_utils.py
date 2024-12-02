import pandas as pd
from dao import get_products_api, get_data_from_api

def load_produtos_data():
    response = get_products_api()
    return pd.DataFrame(response)

def load_artistas_data():
    return pd.read_csv('data/artistas.csv')

def get_data(artists, initial_date, final_date):
    response = get_data_from_api(artists, initial_date, final_date)
    
    df = pd.DataFrame(response)

    prices = {"CAM": 59, "BAG": 19}


    df["quantity"] = df["quantity"].astype(float).astype(int)
    df["unitValue"] = df["unitValue"].astype(float)
        
    df["productSku"] = df["itemSku"].str[:3]
    df["SKU"] = df["itemSku"].str[-8:]
    df["teste"] = df["productSku"].map(prices)

    df["margem"] = df["unitValue"] - df["teste"] - (df["unitValue"] * 0.12)
    grouped = (
        df
        .groupby("itemSku", as_index=False)
        .agg(
            quantidadeVendida=("quantity", "sum"),
            lucroPorModelo=("margem", lambda x: round((x * df.loc[x.index, "quantity"]).sum(), 2)),
            productSku=("productSku", 'max'),
            SKU=("SKU", 'max'),
        )
    )

    result = grouped[["SKU", "productSku","itemSku", "quantidadeVendida", "lucroPorModelo"]]

    result["quantidadeVendida"] = result["quantidadeVendida"].astype(float).astype(int)
    result["lucroPorModelo"] = result["lucroPorModelo"].astype(float)

    return result[result["lucroPorModelo"] > 1]

def prepare_data(relatorio_df, artistas_df, produtos_df):
    # Extrair o código do artista
    relatorio_df['artista'] = relatorio_df['itemSku'].apply(lambda x: x.split('-')[-2])
    
    # Merge com artistas
    merged_df1 = relatorio_df.merge(artistas_df, how='left', left_on='artista', right_on='baseSku')
    
    # Merge com produtos
    merged_df2 = merged_df1.merge(produtos_df[['sku', 'name']], how='left', left_on='itemSku', right_on='sku')

    # Limpeza de nome
    merged_df2['name'] = merged_df2['name'].str.replace('(ESTAMPADA) ', '', regex=False)

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
