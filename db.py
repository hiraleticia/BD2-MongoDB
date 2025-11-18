import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import sqlalchemy
from sqlalchemy.pool import NullPool

@st.cache_resource
def init_connection():
    load_dotenv()
    try:
        # 1. Construir a string de conexão (URI) para o SQLAlchemy
        db_url = (
            f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

        # 2. Criar um engine do SQLAlchemy
        engine = sqlalchemy.create_engine(db_url, poolclass=NullPool, isolation_level="AUTOCOMMIT")
        return engine  # Retorna o engine

    except Exception as e:
        st.error(f"Erro na conexão com SQLAlchemy: {e}")
        return None

@st.cache_data(ttl=3600)
def run_query(query, params=None):
    engine = init_connection()
    if engine is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return pd.DataFrame()
    
    # Usa uma conexão isolada para cada query
    connection = None
    try:
        # 3. pd.read_sql funciona nativamente com o engine do SQLAlchemy
        # Isso elimina o UserWarning
        connection = engine.connect()
        df = pd.read_sql(query, connection, params=params)
        return df

    except Exception as e:
        # Rollback em caso de erro
        if connection:
            try:
                connection.rollback()
            except:
                pass

        st.error(f"Erro na query: {e}")
        return pd.DataFrame()
    
    finally:
        # Sempre fecha a conexão
        if connection:
            try:
                connection.close()
            except:
                pass