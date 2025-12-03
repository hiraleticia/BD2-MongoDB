import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
import queries as q

#--------------------------------------------
#--------------------GERAL-------------------
#--------------------------------------------
def plot_total_musicas():
    return
def plot_total_artistas():
    return

def plot_total_album():
    return

def plot_total_podcast():
    return

def plot_top5_musicas_geral():
    return

def plot_top_10_albuns():
    """
    Mostra o ranking dos 10 álbuns com mais faixas no banco todo.
    FIX: Adicionado tickMinStep=1 para evitar números decimais no eixo.
    """
    try:
        df = q.get_top_10_albuns_com_mais_faixas()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return

    if not df.empty:
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('total_de_musicas',
                    title='Total de Faixas',
                    axis=alt.Axis(format='d', tickMinStep=1) # <--- Correção aqui também
            ),
            y=alt.Y('nome', title='Álbum', sort='-x'),
            color=alt.value("#1E90FF"), # Azul
            tooltip=['nome', 'total_de_musicas']
        ).properties(
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para o ranking.")


def plot_top_5_albuns_salvos():
    return

def plot_top_5_podcasts_seguidos():
    return


#--------------------------------------------
#-------------------ARTISTA------------------
#--------------------------------------------

def plot_artista_mais_seguido():
    return

def plot_artista_mais_mus_publi():
    """Mostra qual artista tem mais músicas cadastradas no sistema."""
    df = q.get_art_mais_mus_publi()

    if not df.empty:
        nome = df.iloc[0]['nome_artista']
        qtd = df.iloc[0]['numero_musicas']

        st.metric(
            label="🥇 Artista com mais músicas publicadas",
            value=nome,
            delta=f"{qtd} Faixas totais"
        )
    else:
        st.warning("Dados indisponíveis.")

def plot_info_artista():
    return


#--------------------------------------------
#-------------------USUARIO------------------
#--------------------------------------------

def plot_total_musicas_user(user_id_logado):
    """Card com o total de músicas diferentes que o usuário ouviu."""
    df = q.get_total_musicas_usuario(user_id_logado)

    total = 0
    if not df.empty:
        total = df.iloc[0]['total_musicas']

    st.metric("🎵 Músicas Diferentes Ouvidas", total)

def plot_tempo_total_escutado(user_id_logado):
    return

def plot_artista_favorito(user_id_logado):
    return

def plot_genero_musica_preferido(user_id_logado):
    return

def plot_musica_favorita(user_id_logado):
    """Card com a música mais ouvida do usuário."""
    df = q.get_top1_musica_ouvida(user_id_logado)

    if not df.empty:
        nome_musica = df.iloc[0]['nome']
        reproducoes = df.iloc[0]['numero_reproducoes']

        st.markdown("**🏆 Sua Música Favorita**")
        st.markdown(f"<h3 style='color: #1ED760;'>{nome_musica}</h3>", unsafe_allow_html=True)
        st.caption(f"Ouvida {reproducoes} vezes")
    else:
        st.info("Você ainda não ouviu nenhuma música.")

def plot_top5_genero_musicas_ouvidas(user_id):
    return

def plot_top5_artistas_ouvidos(user_id_logado):
    return

def plot_top5_musicas_usuario(user_id_logado):
    return



# 1. Listagem de Artistas (Auxiliar para Dropdowns)
def get_lista_artistas():
    """Retorna o DataFrame de artistas para usar em selectboxes no app.py"""
    return q.get_all_artists()

# 2. Contagem de músicas por álbum (Gráfico)
def plot_discografia_artista(id_artista):
    """
    Gera um gráfico de barras mostrando quantas músicas cada álbum tem.
    FIX: Adicionado tickMinStep=1 para evitar números decimais no eixo.
    """
    df = q.get_song_count_per_album(id_artista)

    if not df.empty:
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('total_musicas', 
                    title='Quantidade de Músicas', 
                    # format='d' (inteiro) e tickMinStep=1 (pula de 1 em 1)
                    axis=alt.Axis(format='d', tickMinStep=1) 
            ),
            y=alt.Y('nome_album', title='Álbum', sort='-x'),
            color=alt.value("#1ED760"),  # Verde Spotify
            tooltip=['nome_album', 'total_musicas']
        ).properties(
            title="Músicas por Álbum",
            height=300
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Não foram encontrados álbuns para este artista.")