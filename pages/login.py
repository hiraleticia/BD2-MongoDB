import streamlit as st
import os
from db import init_connection, run_query

# 1. Função para carregar o CSS
def load_css(file_name):
    """Lê um arquivo CSS e o injeta no Streamlit usando st.markdown."""
    try:
        # Tenta construir o caminho para o arquivo CSS
        # Garante que o caminho seja relativo ao local onde o script está rodando
        css_path = os.path.join("styles", file_name) 
        
        with open(css_path, "r") as f:
            css = f.read()
            # Usa st.markdown para injetar o CSS dentro de uma tag <style>
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.error(f"Erro: Arquivo CSS não encontrado em '{css_path}'")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o CSS: {e}")

# Configuração da página (Garante que a barra lateral esteja escondida NO LOGIN)
st.set_page_config(
    page_title="Login - Spotify Dashboard",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed" # ESSENCIAL: Garante que o sidebar não apareça
)

# --- Configuração Inicial de Session State (Importante para evitar KeyErrors) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Se o usuário JÁ estiver logado, redireciona de volta para a Home Page (spotify.py)
if st.session_state.logged_in:
    st.switch_page("app.py") 

# Função de login (chama ao clicar no botão)


def do_login():
    """Lida com a lógica de login verificando as coleções de Usuário e Artista."""

    username_input = st.session_state.input_username.strip()

    if username_input == "":
        st.error("Por favor, digite seu nome de usuário.")
        return

    # Procura dentro do objeto 'conta' pelo campo 'nomeDeUsuario'
    query_filter = {"conta.nomeDeUsuario": username_input}

    try:
        # --- TENTATIVA 1: Verificar na coleção 'usuario' ---
        df_usuario = run_query("usuario", "find_one", query_filter)

        if not df_usuario.empty:
            user_data = df_usuario.iloc[0]
            conta_info = user_data['conta']
            st.session_state.username = conta_info['nomeDeUsuario']
            st.session_state.user_id = int(user_data['idDaConta'])
            st.session_state.user_type = 'usuario'  # Útil para lógica futura
            st.session_state.logged_in = True
            st.switch_page("app.py")
            return

        # --- TENTATIVA 2: Verificar na coleção 'artista' ---
        # Se não achou em usuário, procura em artista
        df_artista = run_query("artista", "find_one", query_filter)

        if not df_artista.empty:
            artist_data = df_artista.iloc[0]

            conta_info = artist_data['conta']
            st.session_state.username = conta_info['nomeDeUsuario']
            st.session_state.user_id = int(artist_data['idDoArtista'])
            st.session_state.user_type = 'artista'
            st.session_state.logged_in = True

            st.switch_page("app.py")
            return

    except Exception as e:
        st.error(f"Erro ao processar login: {e}")
        return

    # Se chegou aqui, não achou em nenhuma das duas coleções
    st.error("Usuário não encontrado. Verifique o nome de usuário.")
    st.session_state.logged_in = False

# CSS personalizado (Mantenha o CSS do seu login.py aqui)
st.markdown("""
<style>
    /* ... (Coloque o CSS do login.py aqui) ... */
    .stApp > header {
        display: none; /* Esconde o cabeçalho padrão do Streamlit */
    }
    /* E o mais importante: Esconde o sidebar no login */
    [data-testid="stSidebar"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# Layout do Formulário de Login (igual ao que eu fiz antes)
st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1]) 

with col2:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<span class='logo-icon'>🎵</span>", unsafe_allow_html=True)
    st.markdown("<h1 class='form-title'>Spotify Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p class='form-subtitle'>Entre para ver sua análise e dados gerais.</p>", unsafe_allow_html=True)

    with st.form("login_form"):
        st.text_input(
            "Nome de Usuário:",
            key="input_username", 
            placeholder="Seu nome de usuário ou artista",
            label_visibility="visible"
        )
        
        st.form_submit_button("Entrar", on_click=do_login, type="primary")

    st.info("O login é apenas pelo nome de usuário para fins do projeto.")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)