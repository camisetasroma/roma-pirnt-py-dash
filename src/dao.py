import requests
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("API_TOKEN")

@st.cache_data
def get_products_api():
    url = f'https://gracoproxy.onrender.com/private/api/products?limit=3000'

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed with status code {response.status_code}")

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