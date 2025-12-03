import pandas as pd
from db import run_query

# ------------ TAB ARTISTA --------------
def get_top3_musicas_art(id_do_artista):

    return run_query()


def get_art_mais_seguidores():
    pipeline = [
        {
            "$project": {
                "nome": "$conta.nome",
                "total_seguidores": {
                    "$size": { "$ifNull": ["$conta.seguidores", []] }
                }
            }
        },
        { "$sort": {"totalSeguidores": -1}},
        { "$limit": 1},
        {
            "$project": {
            "_id": 0,
            "nome": 1
             }
        }
    ]
    return run_query("artista","aggregate",pipeline)


def get_album_mais_salvo_do_artista(id_do_artista):
   
    return run_query()


def check_artist_type(id_artista):
    
    return run_query()

def get_top3_episodios_podcaster(id_artista):
    
    return run_query()


def get_seguidores_podcast_artista(id_artista):
 
    return run_query()


def get_all_episode_plays_by_artist(id_artista):
    
    return run_query()

def get_all_artists():
    #todos os artistas ordenados ordem alfabetica
    #testado e funcionando
    pipeline = [
        {
            "$project": {
                "idDoArtista": 1,
                "nome": "$conta.nome",
                "_id": 0
            }
        },
        { "$sort": { "nome": 1 } }
    ]
    
    return run_query("artista", "aggregate", pipeline)

def get_song_count_per_album(id_artista):
    #conta quantas músicas existem em cada álbum de um artista específico
    #testado e funcionando
    pipeline = [
        { "$match": { "conteudo.idDoArtista": id_artista } },
        
        {
            "$project": {
                "nome_album": "$conteudo.nome",
                "total_musicas": { "$size": "$musicas" },
                "_id": 0
            }
        },
        
        { "$sort": { "total_musicas": -1 } }
    ]
    
    return run_query("album", "aggregate", pipeline)

def get_albums_by_artist(id_artista):
    
    return run_query()

def get_song_plays_by_album(id_album):

    return run_query()

# ------------ TAB GERAL --------------

def get_total_musicas_geral_count():
    pipeline = [
        {"$project": {"qtdMusicas": {"$size": "$musicas"}}},
        {"$group": {"_id": "null", "total": {"$sum": "$qtdMusicas"}}},
        {"$project": {"_id": 0, "total": 1}}
    ]
    return run_query("album", "aggregate", pipeline)

def get_total_artistas_geral_count():
    return run_query("artista", "count_documents",{})

def get_total_album_geral_count():
    return run_query("album", "count_documents",{})

def get_total_podcasts_geral_count():
    return run_query("podcast", "count_documents",{})

def get_top5_musicas_geral():
    return run_query()


def get_top_10_albuns_com_mais_faixas():
    #Retorna os 10 álbuns com maior número de músicas no total
    #testado e funcionando
    pipeline = [
        {
            "$project": {
                "nome": "$conteudo.nome",
                "total_de_musicas": { "$size": "$musicas" },
                "_id": 0
            }
        },
        { "$sort": { "total_de_musicas": -1 } },
        { "$limit": 10 }
    ]
    
    return run_query("album", "aggregate", pipeline)

def get_top5_albuns_salvos():
    pipeline = [
        { "$unwind": "$albumsSalvos" },
        {
            "$group": {
                "_id": "$albumsSalvos.idAlbum",
                "total_salvos": { "$sum": 1}
            }
        },
        { "$sort": { "total_salvos": -1 } },
        { "$limit": 5 },
        {
            "$lookup": {
                "from": "album",
                "localField": "_id",
                "foreignField": "idAlbum",
                "as": "detalhesAlbum"
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_salvos": 1,
                "nome": { "$arrayElemAt": ["$detalhesAlbum.conteudo.nome", 0]}
            }
        }
    ]
    return run_query("usuario", "aggregate", pipeline )


def get_top5_podcast_seguidos():
    pipeline = [
        { "$unwind": "$podcastsSeguidos"},
        {
            "$group": {
            "_id": "$podcastsSeguidos.idPodcast",
            "totalPodcastSeguidos": { "$sum": 1}
        }
        },
        { "$sort": {"totalPodcastSeguidos": -1}},
        { "$limit": 5},
        {
            "$lookup": {
            "from": "podcast",
            "localField": "_id",
            "foreignField": "idPodcast",
            "as": "detalhesPodcast"
            }
        },
        {
            "$project": {
                "_id": 0,
                "nomePodcast": {"$arrayElemAt": ["$detalhesPodcast.conteudo.nome", 0]}
            }
        }
    ]
    return run_query("usuario", "aggregate", pipeline )

def get_art_mais_mus_publi():
    #artista com o maior número de musicas publicadas
    #Busca 2
    #A saída está formata como [ { nome_artista: 'Pietra Fogaça', numero_musicas: 17 } ]
    #testado e funcionando
    
    pipeline = [
        
        {
            "$group": {
                "_id": "$conteudo.idDoArtista",
                "total_musicas": { "$sum": { "$size": "$musicas" } }
            }
        },
        
       
        { "$sort": { "total_musicas": -1 } },
        { "$limit": 1 },
        
        
        {
            "$lookup": {
                "from": "artista",
                "localField": "_id",
                "foreignField": "idDoArtista",
                "as": "dados_artista"
            }
        },
        
    
        {
            "$project": {
                "nome_artista": { "$arrayElemAt": ["$dados_artista.conta.nome", 0] },
                "numero_musicas": "$total_musicas",
                "_id": 0
            }
        }
    ]
    
    return run_query("album", "aggregate", pipeline)


# ------------ TAB USUÁRIO --------------
def get_top1_musica_ouvida(user_id):
    #Retorna a música mais ouvida pelo usuário
    #Testado e funcionando mas cuidado... Foi a que deu mais trabalho
    

    pipeline = [
        # 1. Achar o usuário
        { "$match": { "idDaConta": int(user_id) } },
        
        # 2. Desmontar o array de músicas ouvidas
        { "$unwind": "$conta.musicasOuvidas" },
        
        # 3. Ordenar por reproduções
        { "$sort": { "conta.musicasOuvidas.numeroReproducoes": -1 } },
        
        # 4. Pegar a Top 1
        { "$limit": 1 },
        
        # 5. Buscar o nome da música no álbum (Funciona como um For(For()))
        {
            "$lookup": {
                "from": "album",
                "let": { "id_procurado": "$conta.musicasOuvidas.idDaMusica" },
                "pipeline": [
                    { "$unwind": "$musicas" },
                    { "$match": { "$expr": { "$eq": ["$musicas.idDaMusica", "$$id_procurado"] } } },
                    { "$project": { "nome": "$musicas.nome", "_id": 0 } }
                ],
                "as": "detalhes_da_musica"
            }
        },
        
        # 6. Projetar o resultado final
        {
            "$project": {
                "nome": { "$arrayElemAt": ["$detalhes_da_musica.nome", 0] },
                "numero_reproducoes": "$conta.musicasOuvidas.numeroReproducoes",
                "_id": 0
            }
        }
    ]
    
    return run_query("usuario", "aggregate", pipeline)


def get_top1_art_ouvido(user_id):
   
    return run_query()


def get_genero_musica_ouvida(user_id):
  
    return run_query()

def get_top5_genero_musicas_ouvidas(user_id):
   
    return run_query()


def get_genero_podcast_ouvido(user_id):
  
    return run_query()


def get_total_musicas_usuario(user_id):
    #Retorna o total de músicas diferentes que o usuário já ouviu.
    
    pipeline = [
        { "$match": { "idDaConta": user_id } },
        
        {
            "$project": {
                "total_musicas": { "$size": { "$ifNull": ["$conta.musicasOuvidas", []] } },
                "_id": 0
            }
        }
    ]
    
    return run_query("usuario", "aggregate", pipeline)

def get_top5_artistas_ouvidos(user_id):
   
    return run_query()

def get_top5_musicas_ouvidas(user_id):
    
    return run_query()

def get_tempo_total_escutado_segundos(user_id):
   
    df = run_query()