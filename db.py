import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

@st.cache_resource
def init_connection():
    load_dotenv()
    try:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            st.error("A variável MONGODB_URI não foi encontrada no .env")
            return None

        client = MongoClient(uri)

        # Teste rápido de conexão (ping)
        client.admin.command('ping')
        return client

    except Exception as e:
        st.error(f"Erro na conexão com MongoDB: {e}")
        return None

def get_database():
    """Retorna o database do MongoDB"""
    client = init_connection()
    if client is None:
        return None

    db_name = os.getenv('DB_NAME')
    return client[db_name]

@st.cache_data(ttl=3600)
def run_query(collection_name, operation, *args, **kwargs):
    db = get_database()
    if db is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return pd.DataFrame()

    try:
        collection = db[collection_name]
        # Obtém o método da coleção dinamicamente
        if not hasattr(collection, operation):
            st.error(f"Operação '{operation}' não existe na coleção MongoDB")
            return pd.DataFrame()

        method = getattr(collection, operation)

        # Executa a operação
        result = method(*args, **kwargs)

        # Processa o resultado baseado no tipo de operação
        if operation == 'aggregate':
            # Aggregate retorna um cursor
            df = pd.DataFrame(list(result))

        elif operation == 'find':
            # Find retorna um cursor
            df = pd.DataFrame(list(result))

        elif operation == 'find_one':
            # Find_one retorna um documento único
            if result:
                df = pd.DataFrame([result])
            else:
                df = pd.DataFrame()

        elif operation == 'count_documents':
            # Count retorna um número
            df = pd.DataFrame({'total': [result]})

        elif operation == 'distinct':
            # Distinct retorna uma lista
            df = pd.DataFrame({args[0]: result})

        else:
            # Tenta converter o resultado para DataFrame
            if isinstance(result, (list, tuple)):
                df = pd.DataFrame(result)
            elif isinstance(result, dict):
                df = pd.DataFrame([result])
            elif isinstance(result, (int, float, str)):
                df = pd.DataFrame({'result': [result]})
            else:
                df = pd.DataFrame(list(result))

        # Remove o campo _id se existir
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)

        return df

    except Exception as e:
        st.error(f"Erro na execução da query MongoDB: {e}")
        return pd.DataFrame()