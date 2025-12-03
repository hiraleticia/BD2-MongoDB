import pandas as pd
from db import run_query

# ------------ TAB ARTISTA --------------
def get_top3_musicas_art(id_do_artista):
    pipeline = [
        {"$match": {"conteudo.idDoArtista": id_do_artista}},
        {"$unwind": "$musicas"},
        {"$lookup":
             {"from": "usuario",
              "let": {"musicaId": "$musicas.idDaMusica"},
              "pipeline": [{"$unwind": "$conta.musicasOuvidas"},
                           {"$match": {"$expr": {"$eq": ["$conta.musicasOuvidas.idDaMusica", "$$musicaId"]}}},
                           {"$project": {"_id": 0, "numeroReproducoes": "$conta.musicasOuvidas.numeroReproducoes"}}],
              "as": "reproducoesUsuario"}},
        {"$lookup":
             {"from": "artista",
              "let": {"musicaId": "$musicas.idDaMusica"},
              "pipeline": [{"$unwind": "$conta.musicasOuvidas"},
                           {"$match": {"$expr": {"$eq": ["$conta.musicasOuvidas.idDaMusica", "$$musicaId"]}}},
                           {"$project": {"_id": 0, "numeroReproducoes": "$conta.musicasOuvidas.numeroReproducoes"}}],
              "as": "reproducoesArtista"}},
        {"$group":
             {"_id": "$musicas.idDaMusica",
              "nome": {"$first": "$musicas.nome"},
              "totalReproducoesUsuario": {"$sum": {"$sum": "$reproducoesUsuario.numeroReproducoes"}},
              "totalReproducoesArtista": {"$sum": {"$sum": "$reproducoesArtista.numeroReproducoes"}}}},
        {"$project":
             {"nome": 1,
              "numero_reproducoes": {"$add": ["$totalReproducoesUsuario", "$totalReproducoesArtista"]},
              "_id": 0}
        },
        {"$match": {"numero_reproducoes": {"$gt": 0}}},
        {"$sort": {"numero_reproducoes": -1}},
        {"$limit": 3}
    ]
    return run_query("album", "aggregate", pipeline)


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
        { "$sort": {"total_seguidores": -1}},
        { "$limit": 1},
        {
            "$project": {
            "_id": 0,
            "total_seguidores": 1,
            "nome": 1
             }
        }
    ]
    return run_query("artista","aggregate",pipeline)

# ATUALIZADA
def get_album_mais_salvo_do_artista(id_do_artista):
    """Retorna o álbum mais salvo de um artista específico"""
    pipeline = [
        { "$match": { "conteudo.idDoArtista": id_do_artista } },
        
        { "$lookup": {
            "from": "usuario",
            "let": { "albumId": "$idAlbum" },
            "pipeline": [
                { "$unwind": "$albumsSalvos" },
                { "$match": {
                    "$expr": {
                        "$eq": ["$albumsSalvos.idAlbum", "$$albumId"]
                    }
                }},
                { "$group": {
                    "_id": None,
                    "count": { "$sum": 1 }
                }},
                { "$project": {
                    "_id": 0,
                    "count": 1
                }}
            ],
            "as": "contagemDeSaves"
        }},
        
        { "$addFields": {
            "total_de_vezes_salvo": { "$arrayElemAt": ["$contagemDeSaves.count", 0] }
        }},
        
        { "$match": {
            "total_de_vezes_salvo": { "$gt": 0 }
        }},
        
        { "$project": {
            "_id": 0,
            "nome_do_album": "$conteudo.nome",
            "total_de_vezes_salvo": 1
        }},
        
        { "$sort": { "total_de_vezes_salvo": -1 } },
        
        { "$limit": 1 }
    ]
    return run_query("album", "aggregate", pipeline)


def check_artist_type(id_artista):
    """
        Verifica se o ID fornecido possui documentos nas coleções de podcast ou álbum.
        """

    # 1. Tratamento de Tipo:
    # Baseado nas imagens, os IDs são salvos como Números (Int) no banco.
    # Se o id_artista vier como string ("10"), precisamos converter para int (10).
    try:
        id_busca = int(id_artista)
    except ValueError:
        id_busca = id_artista

    # 2. Definição do Filtro e Projeção
    # O caminho "conteudo.idDoArtista" foi identificado na imagem do álbum.
    query_filter = {"conteudo.idDoArtista": id_busca}
    projection = {"_id": 1}  # Traz apenas o ID para economizar memória (equivale ao SELECT 1)

    # ---------------------------------------------------------
    # 3. Verifica PODCAST
    # Passamos coleção, operação, filtro e projeção
    df_podcast = run_query("podcast", "find_one", query_filter, projection)

    # Usamos .empty porque o run_query retorna um DataFrame
    if not df_podcast.empty:
        return 'podcaster'

    # ---------------------------------------------------------
    # 4. Verifica ÁLBUM
    df_album = run_query("album", "find_one", query_filter, projection)

    if not df_album.empty:
        return 'musico'

    return 'desconhecido'

# ATUALIZADA
def get_top3_episodios_podcaster(id_artista):
    """Retorna os 3 episódios mais reproduzidos de um artista (podcaster)"""
    pipeline = [
        { "$match": { "idDoArtista": id_artista } },
        
        { "$unwind": "$conteudos" },
        
        { "$match": { "conteudos.podcast.idPodcast": { "$exists": True } } },
        
        { "$lookup": {
            "from": "podcast",
            "localField": "conteudos.podcast.idPodcast",
            "foreignField": "idPodcast",
            "as": "podcastInfo"
        }},
        
        { "$unwind": "$podcastInfo" },
        
        { "$unwind": "$podcastInfo.episodios" },
        
        { "$lookup": {
            "from": "usuario",
            "let": { "episodioId": "$podcastInfo.episodios.idEpisodio" },
            "pipeline": [
                { "$unwind": "$conta.episodiosOuvidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$conta.episodiosOuvidos.idEpisodio", "$$episodioId"] }
                }},
                { "$project": { 
                    "_id": 0, 
                    "numeroReproducoes": "$conta.episodiosOuvidos.numeroReproducoes" 
                }}
            ],
            "as": "reproducoesUsuario"
        }},
        
        { "$lookup": {
            "from": "artista",
            "let": { "episodioId": "$podcastInfo.episodios.idEpisodio" },
            "pipeline": [
                { "$unwind": "$conta.episodiosOuvidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$conta.episodiosOuvidos.idEpisodio", "$$episodioId"] }
                }},
                { "$project": { 
                    "_id": 0, 
                    "numeroReproducoes": "$conta.episodiosOuvidos.numeroReproducoes" 
                }}
            ],
            "as": "reproducoesArtista"
        }},
        
        { "$group": {
            "_id": "$podcastInfo.episodios.idEpisodio",
            "nomeArtista": { "$first": "$conta.nome" },
            "nomePodcast": { "$first": "$podcastInfo.conteudo.nome" },
            "nome": { "$first": "$podcastInfo.episodios.nome" },
            "idEpisodio": { "$first": "$podcastInfo.episodios.idEpisodio" },
            "totalReproducoesUsuario": {
                "$sum": { "$sum": "$reproducoesUsuario.numeroReproducoes" }
            },
            "totalReproducoesArtista": {
                "$sum": { "$sum": "$reproducoesArtista.numeroReproducoes" }
            }
        }},
        
        { "$project": {
            "nomeArtista": 1,
            "nomePodcast": 1,
            "nome": 1,
            "idEpisodio": "$_id",
            "numero_reproducoes": {
                "$add": ["$totalReproducoesUsuario", "$totalReproducoesArtista"] 
            }
        }},
        
        { "$sort": { "numero_reproducoes": -1 } },
        
        { "$limit": 3 },
        
        { "$project": {
            "_id": 0,
            "nome": 1,
            "idEpisodio": 1,
            "numero_reproducoes": 1
        }}
    ]    
    return run_query("artista", "aggregate", pipeline)

# ATUALIZADA
def get_seguidores_podcast_artista(id_artista):
    """Retorna os seguidores de cada podcast de um artista"""
    pipeline = [
        { "$match": { "idDoArtista": id_artista } },
        
        { "$unwind": "$conteudos" },
        
        { "$match": { "conteudos.podcast.idPodcast": { "$exists": True } } },
        
        { "$lookup": {
            "from": "podcast",
            "localField": "conteudos.podcast.idPodcast",
            "foreignField": "idPodcast",
            "as": "podcastInfo"
        }},
        
        { "$unwind": "$podcastInfo" },
        
        { "$lookup": {
            "from": "usuario",
            "let": { "podcastId": "$podcastInfo.idPodcast" },
            "pipeline": [
                { "$unwind": "$podcastsSeguidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$podcastsSeguidos.idPodcast", "$$podcastId"] }
                }},
                { "$project": {
                    "idUsuario": "$idDaConta"
                }}
            ],
            "as": "seguidoresUsuarios"
        }},
        
        { "$lookup": {
            "from": "artista",
            "let": { "podcastId": "$podcastInfo.idPodcast" },
            "pipeline": [
                { "$unwind": "$podcastsSeguidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$podcastsSeguidos.idPodcast", "$$podcastId"] }
                }},
                { "$project": {
                    "idArtista": "$idDoArtista"
                }}
            ],
            "as": "seguidoresArtistas"
        }},
        
        { "$project": {
            "_id": 0,
            "nomeArtista": "$conta.nome",
            "nomePodcast": "$podcastInfo.conteudo.nome",
            "total_seguidores": {
                "$add": [
                    { "$size": "$seguidoresUsuarios" },
                    { "$size": "$seguidoresArtistas" }
                ]
            },
            "seguidoresUsuarios": { "$size": "$seguidoresUsuarios" },
            "seguidoresArtistas": { "$size": "$seguidoresArtistas" }
        }},
        
        { "$sort": { "total_seguidores": -1 } }
    ] 
    return run_query("artista", "aggregate", pipeline)

# ATUALIZADA
def get_all_episode_plays_by_artist(id_artista):
    """Retorna todas as reproduções de episódios de um artista"""
    pipeline = [
        { "$match": { "idDoArtista": id_artista } },
        
        { "$unwind": "$conteudos" },
        
        { "$match": { "conteudos.podcast.idPodcast": { "$exists": True } } },
        
        { "$lookup": {
            "from": "podcast",
            "localField": "conteudos.podcast.idPodcast",
            "foreignField": "idPodcast",
            "as": "podcastInfo"
        }},
        
        { "$unwind": "$podcastInfo" },
        
        { "$unwind": "$podcastInfo.episodios" },
        
        { "$lookup": {
            "from": "artista",
            "let": { "episodioId": "$podcastInfo.episodios.idEpisodio" },
            "pipeline": [
                { "$unwind": "$conta.episodiosOuvidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$conta.episodiosOuvidos.idEpisodio", "$$episodioId"] }
                }},
                { "$project": {
                    "numeroReproducoes": "$conta.episodiosOuvidos.numeroReproducoes"
                }}
            ],
            "as": "reproducoesArtistas"
        }},
        
        { "$lookup": {
            "from": "usuario",
            "let": { "episodioId": "$podcastInfo.episodios.idEpisodio" },
            "pipeline": [
                { "$unwind": "$conta.episodiosOuvidos" },
                { "$match": { 
                    "$expr": { "$eq": ["$conta.episodiosOuvidos.idEpisodio", "$$episodioId"] }
                }},
                { "$project": {
                    "numeroReproducoes": "$conta.episodiosOuvidos.numeroReproducoes"
                }}
            ],
            "as": "reproducoesUsuarios"
        }},
        
        { "$group": {
            "_id": "$podcastInfo.episodios.idEpisodio",
            "nomeArtista": { "$first": "$conta.nome" },
            "nomePodcast": { "$first": "$podcastInfo.conteudo.nome" },
            "nome": { "$first": "$podcastInfo.episodios.nome" },
            "numero_reproducoes": {
                "$sum": { 
                    "$add": [
                        { "$sum": "$reproducoesArtistas.numeroReproducoes" },
                        { "$sum": "$reproducoesUsuarios.numeroReproducoes" }
                    ]
                }
            }
        }},
        
        { "$sort": { "numero_reproducoes": -1 } },
        
        { "$project": {
            "_id": 0,
            "nomeArtista": 1,
            "nomePodcast": 1,
            "nome": 1,
            "numero_reproducoes": 1
        }}
    ] 
    return run_query("artista", "aggregate", pipeline)

def get_all_artists():
    #todos os artistas ordenados ordem alfabetica
    #testado e funcionando
    pipeline = [
        {
            "$project": {
                "id_do_artista": "$idDoArtista",
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
    """Retorna todos os álbuns de um artista"""
    pipeline = [
        { "$match": { "idDoArtista": id_artista } },
        
        { "$unwind": "$conteudos" },
        
        { "$match": { "conteudos.album.idAlbum": { "$exists": True } } },
        
        { "$lookup": {
            "from": "album",
            "localField": "conteudos.album.idAlbum",
            "foreignField": "idAlbum",
            "as": "albumInfo"
        }},
        
        { "$unwind": "$albumInfo" },
        
        { "$project": {
            "_id": 0,
            "id_album": "$albumInfo.idAlbum",
            "nome_album": "$albumInfo.conteudo.nome"
        }}
    ]
    return run_query("artista", "aggregate", pipeline)

# ATUALIZADA
def get_song_plays_by_album(id_album):
    """Retorna as reproduções de todas as músicas de um álbum"""
    pipeline = [
        { "$match": { "idAlbum": id_album } },
        
        { "$unwind": "$musicas" },
        
        { "$lookup": {
            "from": "usuario",
            "localField": "musicas.idDaMusica",
            "foreignField": "conta.musicasOuvidas.idDaMusica",
            "as": "usuariosQueOuviram"
        }},
        
        { "$unwind": {
            "path": "$usuariosQueOuviram",
            "preserveNullAndEmptyArrays": True
        }},
        
        { "$unwind": {
            "path": "$usuariosQueOuviram.conta.musicasOuvidas",
            "preserveNullAndEmptyArrays": True
        }},
        
        { "$match": {
            "$or": [
                { "usuariosQueOuviram.conta.musicasOuvidas": { "$exists": False } },
                { "$expr": {
                    "$eq": ["$musicas.idDaMusica", "$usuariosQueOuviram.conta.musicasOuvidas.idDaMusica"]
                }}
            ]
        }},
        
        { "$group": {
            "_id": "$musicas.idDaMusica",
            "musica": { "$first": "$musicas.nome" },
            "reproducoes": {
                "$sum": { 
                    "$ifNull": ["$usuariosQueOuviram.conta.musicasOuvidas.numeroReproducoes", 0] 
                }
            }
        }},
        
        { "$sort": { "reproducoes": -1 } },
        
        { "$project": {
            "_id": 0,
            "musica": 1,
            "reproducoes": 1
        }}
    ]
    return run_query("album", "aggregate", pipeline)

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
    pipeline = [
            { "$unwind": "$musicas"},
            { "$lookup": {
                "from": "usuario",
                "let": {"musicaId": "$musicas.idDaMusica"},
                "pipeline": [
                    { "$unwind": "$conta.musicasOuvidas"},
                        {
                          "$match": {
                          "$expr": {"$eq": ["$conta.musicasOuvidas.idDaMusica", "$$musicaId"]}
                            }
                        },
                    { "$project": {"_id": 0,"numeroReproducoes": "$conta.musicasOuvidas.numeroReproducoes"}}
                ],
                "as":"reproducoesUsuario"}
            },
            { "$lookup": {
                "from": "artista",
                "let": {"musicaId": "$musicas.idDaMusica"},
                "pipeline": [
                    { "$unwind": "$conta.musicasOuvidas"},
                        {
                          "$match": {
                          "$expr": {"$eq": ["$conta.musicasOuvidas.idDaMusica", "$$musicaId"]}
                            }
                        },
                    { "$project": {"_id": 0,"numeroReproducoes": "$conta.musicasOuvidas.numeroReproducoes"}}
                ],
                "as": "reproducoesArtista"}
            },

            { "$group": {
               "_id": "$musicas.idDaMusica",
               "nome_da_musica": { "$first": "$musicas.nome" },
               "nome_do_album": {"$first": "$conteudo.nome"},
                "totalReproducoesUsuario": {
                    "$sum": { "$sum": "$reproducoesUsuario.numeroReproducoes"}
                },

                "totalReproducoesArtista": {
                    "$sum": { "$sum": "$reproducoesArtista.numeroReproducoes"}
                }}
            },
            { "$project": {
                 "nome_da_musica": 1,
                 "nome_do_album": 1,
                 "idDaMusica": "$_id",
                 "total_de_reproducoes": { "$add": ["$totalReproducoesUsuario", "$totalReproducoesArtista"] }
            }},

            { "$sort": {"total_de_reproducoes": -1}},
            { "$limit": 5},
            {"$project": {
                "_id": 0,
                "nome_da_musica": 1,
                "nome_do_album": 1,
                "idDaMusica": "$_id",
                "total_de_reproducoes": 1
            }}
    ]
    return run_query("album","aggregate",pipeline)


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
            "total_seguidores": { "$sum": 1}
        }
        },
        { "$sort": {"total_seguidores": -1}},
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
                "total_seguidores": 1,
                "nome": {"$arrayElemAt": ["$detalhesPodcast.conteudo.nome", 0]}
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
# Nova função para checar se é artista ou usuário
def check_account_type(id_conta):
    try:
        id_ajustado = int(id_conta)
    except ValueError:
        # Se não der para converter para número, mantém como string
        id_ajustado = id_conta
    # 1. Verifica se existe na coleção 'usuario'
    df_usuario = run_query("usuario", "find_one", {"idDaConta": id_ajustado}, {"_id": 1})
    if not df_usuario.empty:
        return 'usuario'
    # 2. Verifica se existe na coleção 'artista'

    df_artista = run_query("artista", "find_one", {"idDoArtista": id_ajustado}, {"_id": 1})
    if not df_artista.empty:
        return 'artista'

    return 'desconhecido'

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
    tipo = check_account_type(user_id)
    if tipo == 'desconhecido':
        return pd.DataFrame()

    colecao = "usuario" if tipo == 'usuario' else "artista"
    campo_id = "idDaConta" if tipo == 'usuario' else "idDoArtista"
    pipeline = [
        {"$match": {campo_id: user_id}},

        # Processar músicas e episódios em paralelo
        {
            "$facet": {
                # Branch 1: Músicas
                "musicas": [
                    {"$unwind": "$conta.musicasOuvidas"},
                    {
                        "$lookup": {
                            "from": "album",
                            "let": {"musicaId": "$conta.musicasOuvidas.idDaMusica"},
                            "pipeline": [
                                {"$match": {"$expr": {"$in": ["$$musicaId", "$musicas.idDaMusica"]}}},
                                {"$project": {"conteudo.idDoArtista": 1}}
                            ],
                            "as": "album"
                        }
                    },
                    {"$unwind": "$album"},
                    {
                        "$project": {
                            "idDoArtista": "$album.conteudo.idDoArtista",
                            "reproducoes": "$conta.musicasOuvidas.numeroReproducoes"
                        }
                    }
                ],

                # Branch 2: Episódios
                "episodios": [
                    {"$unwind": "$conta.episodiosOuvidos"},
                    {
                        "$lookup": {
                            "from": "podcast",
                            "let": {"episodioId": "$conta.episodiosOuvidos.idEpisodio"},
                            "pipeline": [
                                {"$match": {"$expr": {"$in": ["$$episodioId", "$episodios.idEpisodio"]}}},
                                {"$project": {"conteudo.idDoArtista": 1}}
                            ],
                            "as": "podcast"
                        }
                    },
                    {"$unwind": "$podcast"},
                    {
                        "$project": {
                            "idDoArtista": "$podcast.conteudo.idDoArtista",
                            "reproducoes": "$conta.episodiosOuvidos.numeroReproducoes"
                        }
                    }
                ]
            }
        },

        # Combinar resultados
        {
            "$project": {
                "combinado": {"$concatArrays": ["$musicas", "$episodios"]}
            }
        },
        {"$unwind": "$combinado"},

        # Agrupar por artista
        {
            "$group": {
                "_id": "$combinado.idDoArtista",
                "totalReproducoes": {"$sum": "$combinado.reproducoes"}
            }
        },

        {"$sort": {"totalReproducoes": -1}},
        {"$limit": 1},

        # Buscar nome do artista
        {
            "$lookup": {
                "from": "artista",
                "localField": "_id",
                "foreignField": "idDoArtista",
                "as": "artista"
            }
        },
        {"$unwind": "$artista"},

        {
            "$project": {
                "_id": 0,
                "nome": "$artista.conta.nome",
                "totalReproducoes": 1
            }
        }
    ]

    return run_query(colecao, "aggregate", pipeline)

def get_genero_musica_ouvida(user_id):
    """
    Gênero de música mais ouvido
    Funciona para usuário OU artista
    """
    tipo = check_account_type(user_id)

    if tipo == 'desconhecido':
        return pd.DataFrame({'genero': ['N/A']})

    colecao = "usuario" if tipo == 'usuario' else "artista"
    campo_id = "idDaConta" if tipo == 'usuario' else "idDoArtista"

    pipeline = [
        {"$match": {campo_id: user_id}},
        {"$unwind": "$conta.musicasOuvidas"},

        {
            "$lookup": {
                "from": "album",
                "let": {"musicaId": "$conta.musicasOuvidas.idDaMusica"},
                "pipeline": [
                    {"$unwind": "$musicas"},
                    {"$match": {"$expr": {"$eq": ["$musicas.idDaMusica", "$$musicaId"]}}},
                    {"$project": {"genero": "$musicas.genero"}}
                ],
                "as": "musicaInfo"
            }
        },
        {"$unwind": "$musicaInfo"},

        {
            "$group": {
                "_id": "$musicaInfo.genero",
                "reproducoes_totais": {"$sum": "$conta.musicasOuvidas.numeroReproducoes"}
            }
        },

        {"$sort": {"reproducoes_totais": -1}},
        {"$limit": 1},

        {
            "$project": {
                "genero": "$_id",
                "reproducoes_totais": 1
            }
        }
    ]

    return run_query(colecao, "aggregate", pipeline)


def get_top5_genero_musicas_ouvidas(user_id):
    """
    Top 5 gêneros de música mais ouvidos
    """
    tipo = check_account_type(user_id)
    if tipo == 'desconhecido':
        return pd.DataFrame()

    colecao = "usuario" if tipo == 'usuario' else "artista"
    campo_id = "idDaConta" if tipo == 'usuario' else "idDoArtista"

    pipeline = [
        {"$match": {campo_id: user_id}},
        {"$unwind": "$conta.musicasOuvidas"},

        {
            "$lookup": {
                "from": "album",
                "let": {"musicaId": "$conta.musicasOuvidas.idDaMusica"},
                "pipeline": [
                    {"$unwind": "$musicas"},
                    {"$match": {"$expr": {"$eq": ["$musicas.idDaMusica", "$$musicaId"]}}},
                    {"$project": {"genero": "$musicas.genero"}}
                ],
                "as": "musicaInfo"
            }
        },
        {"$unwind": "$musicaInfo"},

        {
            "$group": {
                "_id": "$musicaInfo.genero",
                "reproducoes_totais": {"$sum": "$conta.musicasOuvidas.numeroReproducoes"}
            }
        },

        {"$sort": {"reproducoes_totais": -1}},
        {"$limit": 5},

        {
            "$project": {
                "_id": 0,
                "genero": "$_id",
                "reproducoes_totais": 1
            }
        }
    ]

    return run_query(colecao, "aggregate", pipeline)

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
    """
    Top 5 artistas mais ouvidos (músicas + podcasts)
    """
    tipo = check_account_type(user_id)
    if tipo == 'desconhecido':
        return pd.DataFrame()

    colecao = "usuario" if tipo == 'usuario' else "artista"
    campo_id = "idDaConta" if tipo == 'usuario' else "idDoArtista"
    pipeline = [
        {"$match": {campo_id: user_id}},

        {
            "$facet": {
                "musicas": [
                    {"$unwind": "$conta.musicasOuvidas"},
                    {
                        "$lookup": {
                            "from": "album",
                            "let": {"musicaId": "$conta.musicasOuvidas.idDaMusica"},
                            "pipeline": [
                                {"$match": {"$expr": {"$in": ["$$musicaId", "$musicas.idDaMusica"]}}},
                                {"$project": {"conteudo.idDoArtista": 1}}
                            ],
                            "as": "album"
                        }
                    },
                    {"$unwind": "$album"},
                    {
                        "$project": {
                            "idDoArtista": "$album.conteudo.idDoArtista",
                            "reproducoes": "$conta.musicasOuvidas.numeroReproducoes"
                        }
                    }
                ],

                "episodios": [
                    {"$unwind": "$conta.episodiosOuvidos"},
                    {
                        "$lookup": {
                            "from": "podcast",
                            "let": {"episodioId": "$conta.episodiosOuvidos.idEpisodio"},
                            "pipeline": [
                                {"$match": {"$expr": {"$in": ["$$episodioId", "$episodios.idEpisodio"]}}},
                                {"$project": {"conteudo.idDoArtista": 1}}
                            ],
                            "as": "podcast"
                        }
                    },
                    {"$unwind": "$podcast"},
                    {
                        "$project": {
                            "idDoArtista": "$podcast.conteudo.idDoArtista",
                            "reproducoes": "$conta.episodiosOuvidos.numeroReproducoes"
                        }
                    }
                ]
            }
        },

        {
            "$project": {
                "combinado": {"$concatArrays": ["$musicas", "$episodios"]}
            }
        },
        {"$unwind": "$combinado"},

        {
            "$group": {
                "_id": "$combinado.idDoArtista",
                "reproducoes_totais": {"$sum": "$combinado.reproducoes"}
            }
        },

        {"$sort": {"reproducoes_totais": -1}},
        {"$limit": 5},

        {
            "$lookup": {
                "from": "artista",
                "localField": "_id",
                "foreignField": "idDoArtista",
                "as": "artista"
            }
        },
        {"$unwind": "$artista"},

        {
            "$project": {
                "_id": 0,
                "nome": "$artista.conta.nome",
                "reproducoes_totais": 1
            }
        }
    ]
    return run_query(colecao, "aggregate", pipeline)

def get_top5_musicas_ouvidas(user_id):
    pipeline = [
        {
            "$match": {"idDaConta": user_id}
        },
        {"$unwind": "$conta.musicasOuvidas"},
        {
            "$lookup": {
                "from": "album",
                "localField": "conta.musicasOuvidas.idDaMusica",
                "foreignField": "musicas.idDaMusica",
                "as": "dadosAlbum"
            }
        },
        {"$unwind": "$dadosAlbum"},
        {"$unwind": "$dadosAlbum.musicas"},
        {
            "$match": {
                "$expr": {
                    "$eq": ["$dadosAlbum.musicas.idDaMusica", "$conta.musicasOuvidas.idDaMusica"]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "nome": "$dadosAlbum.musicas.nome",
                "numero_reproducoes": "$conta.musicasOuvidas.numeroReproducoes"
            }
        },
        {
            "$sort": {
                "numero_reproducoes": -1
            }
        },
        {
            "$limit": 5
        }
    ]
    return run_query("usuario", "aggregate", pipeline)

def get_tempo_total_escutado_segundos(user_id):
    tipo = check_account_type(user_id)
    if tipo == 'desconhecido':
        return 0

    colecao = "usuario" if tipo == 'usuario' else "artista"
    campo_id = "idDaConta" if tipo == 'usuario' else "idDoArtista"

    pipeline = [
        {"$match":{campo_id:user_id}},
        {"$unwind":"$conta.musicasOuvidas"},
        {"$lookup":
        {
            "from":"album",
            "let":{"musica_id":"$conta.musicasOuvidas.idDaMusica"},
            "pipeline":[
                {
                    "$match":{"$expr":{"$in":["$$musica_id","$musicas.idDaMusica"]}}
                },
                {"$unwind":"$musicas"},
                {"$match":{"$expr":{"$eq":["$musicas.idDaMusica","$$musica_id"]}}},
                {"$project":{"tempoDeDuracaoMS":{"$convert":{"input":"$musicas.tempoDeDuracao","to":"long","onError":0,"onNull":0}}}}
            ],
            "as":"duracaoInfo"
        }
        },
        {"$unwind":"$duracaoInfo"},
        {"$group":{"_id":"null","tempoTotalMS":{"$sum":{"$multiply":["$duracaoInfo.tempoDeDuracaoMS","$conta.musicasOuvidas.numeroReproducoes"]}}}},
        {"$project":{"_id":0,"tempoTotalMS":1,"total_segundos":{"$divide":["$tempoTotalMS",1000]}}}
    ]

    df = run_query(colecao,"aggregate", pipeline)


    # Tratamento de erro / vazio
    if df.empty or "total_segundos" not in df.columns:
        return 0

    # Retorna o valor inteiro (convertendo de float se necessário)
    return int(df.iloc[0]['total_segundos'])