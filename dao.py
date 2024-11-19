import psycopg2
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# Set your database connection parameters
host = os.getenv("DATABASE_URL") 
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
port = os.getenv("DB_PORT")

@st.cache_data
def get_data(initial_date, final_fate):
    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port,
        sslmode = "require"
    )

    # Define your SQL query
    query = f"""SELECT 
        RIGHT(item_sku, 8) AS SKU
        ,item_sku
        ,ROUND(SUM(quantity)::NUMERIC, 0) AS quantidade_vendida
        ,ROUND(SUM(margem*quantity)::NUMERIC, 2) AS lucro_por_modelo
    FROM (
        SELECT
            erp_order_number,
            item_sku,
            quantity,
            unit_value,
            59.00 AS "preço camiseta",
            CAST((unit_value / 100 * 12) AS FLOAT) AS "imposto (12%)",
            CAST(unit_value - 59.00 - (unit_value / 100 * 12) AS FLOAT) AS margem
        FROM sold_items si
        LEFT JOIN orders o ON si.order_id = o.id
        WHERE 1=1
            AND o.status NOT IN ('C', 'O')
            AND o.order_date BETWEEN '{initial_date}' AND '{final_fate}'
            AND item_sku LIKE 'CAM-%-%-%-%-%'
        ORDER BY erp_order_number
    )
    GROUP BY item_sku;"""

    # Load the result of the query into a pandas DataFrame
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

