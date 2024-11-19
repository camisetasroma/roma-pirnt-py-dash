import streamlit as st
from dash import render_dash, log_out, login

# Função de login
def render():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        log_out()
        render_dash()
        return

    login()

# Chamar a função de login
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False  # Inicializa o estado de login

    render()