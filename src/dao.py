import requests
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("API_TOKEN")

@st.cache_data
def get_data_from_api(artists, initial_date, final_date):
    url = f'https://gracoproxy.onrender.com/private/api/get-romaprint-sales'

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "artists": artists,
        "startDate": initial_date.strftime("%Y-%m-%d"),
        "endDate": final_date.strftime("%Y-%m-%d")
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed with status code {response.status_code}")

def get_data(artists, initial_date, final_date):
    response = get_data_from_api(artists, initial_date, final_date)
    
    df = pd.DataFrame(response)
    df["quantity"] = df["quantity"].astype(float).astype(int)
    df["unitValue"] = df["unitValue"].astype(float)
    df["margem"] = df["unitValue"] - 59 - (df["unitValue"]/(100 * 12))
    
    grouped = (
        df
        .groupby("itemSku", as_index=False)
        .agg(
            quantidadeVendida=("quantity", "sum"),
            lucroPorModelo=("margem", lambda x: round((x * df.loc[x.index, "quantity"]).sum(), 2))
        )
    )

    grouped["SKU"] = grouped["itemSku"].str[-8:]
    result = grouped[["SKU", "itemSku", "quantidadeVendida", "lucroPorModelo"]]

    result["quantidadeVendida"] = result["quantidadeVendida"].astype(float).astype(int)
    result["lucroPorModelo"] = result["lucroPorModelo"].astype(float)

    return result[result["lucroPorModelo"] > 2]