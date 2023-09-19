import streamlit as st
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import pandas as pd
import numpy as np
import json

@st.cache_resource
def elastic_connection(url: str) -> Elasticsearch:
    es = Elasticsearch(hosts=url)
    
    return es

def load_indices_from_elastic(elastic_url: str):
    
    es = elastic_connection(elastic_url)
    indices = es.indices.get_alias(index="*")
    
    indices_lst = [indice for indice in indices.keys() if 'kibana' not in indice]
    
    st.session_state["indices_elastic_list_options"] = indices_lst

# @st.cache_data    
def load_dataframe(json_data: dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(json_data)

def get_records_to_upload(dataframe: pd.DataFrame, indice_name: str) -> list:
    records = dataframe.to_dict(orient='records')
    
    records_bulk = [
        {
            '_index': indice_name,
            '_source': {**doc, **{'timestamp': datetime.now()}}
        }
        for doc in records
    ]
    
    return records_bulk

def upload_bulk_to_elastic(es:Elasticsearch, records_bulk: list):
    try:
        bulk(es, records_bulk)
    except Exception as ex:
        print("Error: ", ex)
        raise ex
    
def start_upload_to_elastic(dataframe: pd.DataFrame, selected_file: str, indice_name: str, elastic_url: str):
    
    if selected_file and indice_name:
        
        df_copy = dataframe.copy(deep=True)
        print(df_copy.shape)
        try:
            es = elastic_connection(elastic_url)
            df_copy = df_copy.replace('nulo', np.nan)
            df_copy = df_copy.dropna(how='all')
            df_copy = df_copy.drop_duplicates()
            df_copy = df_copy.replace([np.nan], [None])
            df_copy.loc[:, 'DATA_INICIAL_PROPOSTA'] = pd.to_datetime(df_copy['DATA_INICIAL_PROPOSTA'], format="%Y%m%d")
            df_copy.loc[:, 'DATA_FINAL_PROPOSTA'] = pd.to_datetime(df_copy['DATA_FINAL_PROPOSTA'], format="%Y%m%d")
            df_copy.loc[:, 'DATA_HOMOLOGACAO'] = pd.to_datetime(df_copy['DATA_HOMOLOGACAO'], format="%Y%m%d")
            df_copy = df_copy.dropna(subset=['DATA_INICIAL_PROPOSTA', 'DATA_FINAL_PROPOSTA', 'DATA_HOMOLOGACAO'])
            print(df_copy.shape)
            
            records_bulk = get_records_to_upload(df_copy, indice_name)
            upload_bulk_to_elastic(es, records_bulk)
            st.success('File Uploaded!', icon="✅")
            
        except Exception as ex:
            print("Error: ", ex)
    else:
        st.warning("Você precisa carregar um arquivo e escolher um índice antes de iniciar um upload!", icon="🚨")

st.set_page_config(page_title="Carregar Documento")

elastic_url = st.sidebar.text_input("Elastic URL", 'http://localhost:9200', help='O endereço onde está localizado o Elastic.')

if "indices_elastic_list_options" not in st.session_state:
    st.session_state["indices_elastic_list_options"] = []

select_operation = st.sidebar.selectbox('Operação', options=['Criar', 'Atualizar'])
if select_operation == 'Criar':
    indice_name = st.sidebar.text_input('Novo índice:', help='Caso deseje criar um novo índice, insira seu nome e clique em Criar.', key='indice_txt_input')
    
elif select_operation == 'Atualizar':    
    indice_name = st.sidebar.selectbox("Carregar para índice:", options=st.session_state.indices_elastic_list_options, key='index_dropdown', help='Selecione um índice caso desejo adicionar dados a ele.')
    btn_load_indices = st.sidebar.button('Carregar índices', on_click=load_indices_from_elastic, kwargs={'elastic_url': elastic_url})
   
print(indice_name)
uploaded_file = st.sidebar.file_uploader('Carregar arquivo:', type=['json'])
if uploaded_file:
    js_file = json.load(uploaded_file)
    df = load_dataframe(js_file)
    st.dataframe(df)
else:
    df = None

btn_create_indices = st.sidebar.button('Iniciar upload', on_click=start_upload_to_elastic, kwargs={'dataframe': df, 'selected_file': uploaded_file, 'indice_name': indice_name, 'elastic_url': elastic_url})