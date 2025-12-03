import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
import queries as q

# ==============================================================================
#  Funções Novas Nikolas (MongoDB)
#  
# ==============================================================================

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

#3. Top 10 Álbuns com mais Faixas (Gráfico)
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

# 4. Música Favorita do Usuário (Métrica)
def plot_musica_favorita(user_id):
    """Card com a música mais ouvida do usuário."""
    df = q.get_top1_musica_ouvida(user_id)
    
    if not df.empty:
        nome_musica = df.iloc[0]['nome']
        reproducoes = df.iloc[0]['numero_reproducoes']
        
        st.markdown("**🏆 Sua Música Favorita**")
        st.markdown(f"<h3 style='color: #1ED760;'>{nome_musica}</h3>", unsafe_allow_html=True)
        st.caption(f"Ovida {reproducoes} vezes")
    else:
        st.info("Você ainda não ouviu nenhuma música.")

# 5. Total de Músicas do Usuário (Métrica)
def plot_total_musicas_user(user_id):
    """Card com o total de músicas diferentes que o usuário ouviu."""
    df = q.get_total_musicas_usuario(user_id)
    
    total = 0
    if not df.empty:
        total = df.iloc[0]['total_musicas']
        
    st.metric("🎵 Músicas Diferentes Ouvidas", total)

# 6. Artista com mais Publicações (Métrica)
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


# ==============================================================================
#  FUNÇÕES ANTIGAS (SQL) - PENDENTES DE MIGRAÇÃO 
#  Estão comentadas para não quebrar o código
# ==============================================================================

'''
def plot_total_musicas():
    df_total_musicas = q.get_total_musicas_geral_count()
    total_musicas = df_total_musicas.iloc[0]['total'] if not df_total_musicas.empty else 0
    st.metric("🎵 Total de músicas", total_musicas)

def plot_total_artistas():
    df_total_artistas = q.get_total_artistas_geral_count()
    total_musicas = df_total_artistas.iloc[0]['total'] if not df_total_artistas.empty else 0
    st.metric("👥 Total de artistas", total_musicas)

def plot_total_album():
    df_total_album = q.get_total_album_geral_count()
    total_album = df_total_album.iloc[0]['total'] if not df_total_album.empty else 0
    st.metric("📀 Total de álbuns", total_album)

def plot_total_podcast():
    df_total_podcast = q.get_total_podcasts_geral_count()
    total_podcast = df_total_podcast.iloc[0]['total'] if not df_total_podcast.empty else 0
    st.metric("🎙️ Total de podcasts", total_podcast)

def plot_top5_musicas_geral():
    try:
        df_top_musicas = q.get_top5_musicas_geral()
    except Exception as e:
        st.error(f"Erro ao buscar os dados do banco de dados: {e}")
        df_top_musicas = pd.DataFrame()

    if not df_top_musicas.empty:
        chart = alt.Chart(df_top_musicas).mark_bar().encode(
            x=alt.X('total_de_reproducoes', title='Total de Reproduções', axis=alt.Axis(format=',')),
            y=alt.Y('nome_da_musica', title='Música', sort='-x'),
            color=alt.Color('nome_do_album', title='Álbum', legend=alt.Legend(orient="bottom")),
            tooltip=[alt.Tooltip('nome_da_musica'), alt.Tooltip('nome_do_album'), alt.Tooltip('total_de_reproducoes')]
        ).properties(height=350, background='transparent').interactive()
        st.altair_chart(chart, use_container_width=True, theme=None)
    else:
        st.info("Nenhum dado encontrado para as Top 5 músicas.")

def plot_top_5_albuns_salvos():
    try:
        df_top_albuns_salvos = q.get_top5_albuns_salvos()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        df_top_albuns_salvos = pd.DataFrame()

    if not df_top_albuns_salvos.empty:
        df_top_albuns_salvos = df_top_albuns_salvos.sort_values(by='total_salvos', ascending=False)
        chart = alt.Chart(df_top_albuns_salvos).mark_bar().encode(
            x=alt.X('total_salvos', title='Total de Salvamentos'),
            y=alt.Y('nome', title='Nome do Álbum', sort='-x'),
            color=alt.value("#FF66B2")
        ).properties(height=300, background='transparent').interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Nenhum dado de álbum salvo encontrado.")

def plot_top_5_podcasts_seguidos():
    try:
        df_top_podcasts = q.get_top5_podcast_seguidos()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        df_top_podcasts = pd.DataFrame()

    if not df_top_podcasts.empty:
        df_top_podcasts = df_top_podcasts.sort_values(by='total_seguidores', ascending=False)
        chart = alt.Chart(df_top_podcasts).mark_bar().encode(
            x=alt.X('total_seguidores', title='Total de Seguidores'),
            y=alt.Y('nome', title='Nome do Podcast', sort='-x'),
            color=alt.value("#9B59B6")
        ).properties(height=300, background='transparent').interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Nenhum dado de podcast seguido encontrado.")

def plot_artista_mais_seguido():
    df_mais_seguidores = q.get_art_mais_seguidores()
    if not df_mais_seguidores.empty:
        artista_nome = df_mais_seguidores.iloc[0]['nome']
        seguidores = df_mais_seguidores.iloc[0]['total_seguidores']
        st.metric(label="Artista com mais seguidores", value=artista_nome, delta=f"{seguidores} seguidores")
    else:
        st.info("Não foi possível carregar o artista com mais seguidores.")

def plot_info_artista():
    # Esta função era complexa e dependia de várias queries SQL.
    # Precisa ser refatorada completamente usando a lógica do MongoDB (get_all_artists já existe).
    pass

def plot_tempo_total_escutado(user_id_logado):
    total_segundos = q.get_tempo_total_escutado_segundos(user_id_logado)
    if total_segundos is None: total_segundos = 0
    total_minutos = total_segundos // 60
    horas = total_minutos // 60
    minutos = total_minutos % 60
    st.metric("Horas ouvindo", f"{horas}h {minutos}m")

def plot_artista_favorito(user_id_logado):
    df_art_fav = q.get_top1_art_ouvido(user_id_logado)
    artista_fav = df_art_fav.iloc[0]['nome'] if not df_art_fav.empty else 
'''