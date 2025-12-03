import streamlit as st
import altair as alt
import plotly.express as px
from dotenv import load_dotenv
import os
from db import run_query
import plot_querys as pq

# ----------------------------------------
# 1. Função para carregar o CSS
# ----------------------------------------
def load_css(file_name):
    """Lê um arquivo CSS e o injeta no Streamlit usando st.markdown."""
    try:
        css_path = os.path.join("assets/styles", file_name) 
        with open(css_path, "r") as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Erro: Arquivo CSS não encontrado em '{css_path}'")
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o CSS: {e}")

# ----------------------------------------
# 2. Funções e Verificação de Login
# ----------------------------------------

st.set_page_config(
    page_title="Dashboard Análise do Spotify",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = "Usuário Convidado"

if not st.session_state.logged_in:
    st.switch_page("pages/login.py") 

def do_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.switch_page("pages/login.py")

# ----------------------------------------
# 3. Carregamento do CSS e Layout
# ----------------------------------------
load_css("app.css") 

with st.container():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<h4 style='color: #1ED760;'>👤 Logado como: {st.session_state.username}</h4>", unsafe_allow_html=True)
    with col2:
        st.button("🚪 Sair", type="secondary", on_click=do_logout)
        
st.markdown("<h1 class='main-title'>Dashboard para análise Spotify</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    st.markdown("<p class='image-label'>Um dashboard sobre uma aplicação análoga ao Spotify (Versão MongoDB)</p>", unsafe_allow_html=True)

# Sistema de Tabs
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🎤 Análise Artistas", "👤 Análise do Usuário"])


# ==============================================================================
# TAB 1: Visão Geral
# ==============================================================================
with tab1:
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.header("📊 Visão Geral")

    col1, col2 = st.columns(2)

    with col1:
        # --- FUNÇÕES SQL ANTIGAS (COMENTADAS) ---
        # pq.plot_total_musicas()
        # pq.plot_total_artistas()
        st.info("🚧 Top 5 Músicas (Em migração para MongoDB)")
        # pq.plot_top5_musicas_geral()
        
        st.info("🚧 Álbuns mais salvos (Em migração para MongoDB)")
        # pq.plot_top_5_albuns_salvos()

    with col2:
        # --- FUNÇÕES SQL ANTIGAS (COMENTADAS) ---
        # pq.plot_total_album()
        # pq.plot_total_podcast()

        st.subheader("Top 10 álbuns com mais Faixas 💿")
        # --- FUNÇÃO NOVA MONGODB ✅ ---
        pq.plot_top_10_albuns()
        
        st.info("🚧 Podcasts mais seguidos (Em migração para MongoDB)")
        # pq.plot_top_5_podcasts_seguidos()

    st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# TAB 2: Análise de Artistas
# ==============================================================================
with tab2:
    st.header("🎤 Análise dos Artistas")
    st.subheader("Destaques da Categoria")
    
    col1, col2 = st.columns(2)
    with col1:
        # pq.plot_artista_mais_seguido() (ANTIGO)
        st.info("🚧 Artista com mais seguidores (Em migração)")
        
    with col2:
        # --- FUNÇÃO NOVA MONGODB ✅ ---
        pq.plot_artista_mais_mus_publi()

    st.markdown("---")
    
    # --- NOVA LÓGICA DE SELEÇÃO DE ARTISTA (ADAPTADA PARA O NOVO PLOT_QUERYS) ---
    st.subheader("Selecione um artista para análise")
    
    # Busca a lista de artistas usando a query nova
    df_artistas = pq.get_lista_artistas()
    
    if not df_artistas.empty:
        artista_escolhido = st.selectbox(
            "Digite para filtrar artistas:",
            df_artistas["nome"].tolist()
        )
        
        # Pega o ID do artista selecionado
        id_artista = int(df_artistas[df_artistas["nome"] == artista_escolhido]["idDoArtista"].iloc[0])
        
        st.success(f"Artista selecionado: {artista_escolhido}")
        
        # --- FUNÇÃO NOVA MONGODB ✅ ---
        st.subheader(f"Discografia de {artista_escolhido}")
        pq.plot_discografia_artista(id_artista)
        
        # --- CÓDIGO ANTIGO COMPLEXO (COMENTADO POR ENQUANTO) ---
        '''
        artist_type = q.check_artist_type(id_artista)
        if artist_type == 'musico':
            # ... Lógica antiga de músico ...
            pass
        elif artist_type == 'podcaster':
            # ... Lógica antiga de podcaster ...
            pass
        '''
        st.info("ℹ️ Outras métricas detalhadas (gênero, reproduções por música, tipo de artista) estão sendo migradas do SQL.")
        
    else:
        st.warning("Não foi possível carregar a lista de artistas.")


# ==============================================================================
# TAB 3: Análise do Usuário
# ==============================================================================
with tab3:
    user_id_logado = st.session_state.user_id
    username_logado = st.session_state.username

    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.header(f"👤 Análise de {st.session_state.username}")
    st.subheader("Suas estatísticas pessoais")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # --- FUNÇÃO NOVA MONGODB ✅ ---
        pq.plot_total_musicas_user(user_id_logado)

    with col2:
        # pq.plot_tempo_total_escutado(user_id_logado) (ANTIGO)
        st.write("⏱️ (Em breve)")

    with col3:
        # pq.plot_genero_musica_preferido(user_id_logado) (ANTIGO)
        st.write("🎵 (Em breve)")

    with col4:
        # --- FUNÇÃO NOVA MONGODB ✅ ---
        pq.plot_musica_favorita(user_id_logado)

    with col5:
        # pq.plot_artista_favorito(user_id_logado) (ANTIGO)
        st.write("⭐ (Em breve)")

    st.markdown("---")

    st.subheader("📈 Análise de estatísticas")
    st.info("🚧 Gráficos detalhados do usuário (Top 5 gêneros, artistas, histórico) em migração.")
    
    # with st.expander("Ver estatísticas detalhadas"):
    #     pq.plot_top5_musicas_usuario(user_id_logado)
    #     col1, col2 =st.columns(2)
    #     with col1:
    #         pq.plot_top5_genero_musicas_ouvidas(user_id_logado)
    #     with col2:    
    #         pq.plot_top5_artistas_ouvidos(user_id_logado)

    st.markdown("</div>", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Dashboard Spotify Analytics © 2025 (MongoDB Edition)</p>",
    unsafe_allow_html=True
)