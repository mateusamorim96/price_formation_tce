from dotenv import load_dotenv
import os
import re
from unidecode import unidecode

from elasticsearch import Elasticsearch

import pandas as pd

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

st.set_page_config(page_title="Formação de Preços", page_icon="💲")

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ['gpt_api_key']

template_similar_words = """Desejo comprar um material e gostaria de buscar por diferentes variações no nome desse material para amplificar o sucesso de encontrar muitos resultados.
Por exemplo, eu desejo comprar uma calculadora e te faço o seguinte pedido: Gostaria de sinônimos para a palavra 'caneta esferográfica', separados por vírgula. 
O que eu espero como resposta: caneta esferográfica, tinteiro, caneta de ponta fina, caneta nanquim, caneta hidrográfica. 
O que eu não espero como resposta: lápis, lapiseira, pincel, marca texto.
Dessa forma, eu gostaria de sinônimos para a palavra '{desirable_item}', separados por vígula."""

template_validate_items = """Gostaria de saber quais itens dessa lista de materiais {lista_itens_base_dados}, em formato Python, são relacionadas com essa lista de itens desejados {lista_item_desejado} e que são referentes a compra/aquisição.
Para identificar se são referentes a compras a lista de materiais deve conter palavras relacionadas a itens, como sua descrição, características, medidas, etc.
Para identificar se não são referentes a compras a lista de materiais provalmente conterá palavras que indiquem prestação de serviços e termos não relacionados a compras.
Dessa forma, eu gostaria que me retornasse as posições da lista de materiais que estão relacionados com compras/aquisição de materiais em formato de lista Python. Apenas a lista com as posições, sem texto."""

def elastic_connection(url: str) -> Elasticsearch:
    es = Elasticsearch(hosts=url)
    
    return es

def load_indices_from_elastic(elastic_url: str):
    
    es = elastic_connection(elastic_url)
    indices = es.indices.get_alias(index="*")
    
    indices_lst = [indice for indice in indices.keys() if 'kibana' not in indice]
    
    st.session_state["indices_elastic_list_options_page1"] = indices_lst
    
def load_fields_from_indices(elastic_url: str, indice: str):
    
    try:
        es = elastic_connection(elastic_url)    
        
        fields = list(es.indices.get_mapping(indice)[indice]['mappings']['properties'].keys())

        st.session_state["elastic_indices_field_list_options"] = fields
    except Exception as ex:
        st.warning(ex)
        
def query_database(elastic_url: str, indice: str, field: str, query_items: list):
    es = elastic_connection(elastic_url)
    
    records = list()
    
    string_query = " ".join(f"({unidecode(item.strip())})" for item in query_items)
    
    resp = es.search(index=indice, size=-1, body={
    "query": {
        "query_string": {
        "query": string_query,
        "default_field": field
        }
    },
    "track_total_hits": True
    })
    
    for hit in resp['hits']['hits']:
        records.append(hit["_source"])
    
    print("records len: ", len(records))
    return records

def print_item_field(item, item_suggestions, elastic_url):
    global similar_words_dropdown
    print("Chamando pelo botão")
    suggestions = item_suggestions.run(item)
    print(suggestions)
    similar_words_lst = suggestions.strip().split(',')
    st.session_state["similar_words_lst_options"] = similar_words_lst
    
    load_indices_from_elastic(elastic_url)
    
def get_llm(temperature):
    
    return OpenAI(temperature=temperature)

st.title("TCE Price Formation")

elastic_url = st.sidebar.text_input("Elastic URL", 'http://localhost:9200', help='O endereço onde está localizado o Elastic.')

if "similar_words_lst_options" not in st.session_state:
    st.session_state["similar_words_lst_options"] = []

desirable_item = st.sidebar.text_input("Item desejado")
temperature_slider = st.sidebar.slider("Criatividade sinônimos", 0, 100, 60, 5, help="Quanto maior a criatividade, maior o risco que o GPT assume de errar.")

llm = get_llm(temperature_slider / 100)
prompt_suggestion_names = PromptTemplate(input_variables = ['desirable_item'], template = template_similar_words)
item_suggestions_llm = LLMChain(llm=llm, prompt=prompt_suggestion_names, output_key="suggestions")

btn_search_related_words = st.sidebar.button("Pesquisar", on_click=print_item_field, kwargs={"item": desirable_item, "item_suggestions": item_suggestions_llm, "elastic_url": elastic_url})

similar_words_dropdown = st.sidebar.multiselect("Termos associados", options=st.session_state.similar_words_lst_options, key='suggestion_dropdown')

if "indices_elastic_list_options_page1" not in st.session_state:
    st.session_state["indices_elastic_list_options_page1"] = []
    
if "elastic_indices_field_list_options" not in st.session_state:
    st.session_state["elastic_indices_field_list_options"] = []
    
indice_name = st.sidebar.selectbox("Carregar campos do indice:", options=st.session_state.indices_elastic_list_options_page1, key='index_dropdown', help='Selecione o indice que deseja realizar a busca.')
load_fields_from_indices(elastic_url, indice_name)

selected_field = st.sidebar.selectbox("Selecione um campo:", options=st.session_state.elastic_indices_field_list_options, help='Selecione o campo que contém a informação de interesse.')

temperature_slider_validate_items = st.sidebar.slider("Criatividade validação", 0, 100, 60, 5, help="Quanto maior a criatividade, maior o risco que o GPT assume de errar.")
btn_load_from_elastic = st.sidebar.button("Consultar base de dados")

if btn_load_from_elastic:
    records = query_database(elastic_url=elastic_url, indice=indice_name, field=selected_field, query_items=similar_words_dropdown)
    df = pd.DataFrame.from_records(records)
    
    item_names_lst = df[selected_field].values.tolist()
    prompt_validation_items = PromptTemplate(input_variables = ['lista_itens_base_dados', 'lista_item_desejado'], template = template_validate_items)
    validate_item_names_llm = LLMChain(llm=llm, prompt=prompt_validation_items, output_key="suggested_items")
    validation_position_list = validate_item_names_llm.run(lista_itens_base_dados=item_names_lst, lista_item_desejado=similar_words_dropdown)
    numbers_lst = re.findall(r'\d+', validation_position_list)
    validation_position_list = [int(number) for number in numbers_lst]
    
    print(df.shape)
    st.session_state.elastic_df = df
    st.session_state.validation_position_list = validation_position_list
    

if st.session_state.get('elastic_df') is not None:
    df = st.session_state.get('elastic_df')
    gb = GridOptionsBuilder.from_dataframe(st.session_state.get('elastic_df'))
    gb.configure_selection(selection_mode="multiple", use_checkbox=True, pre_selected_rows=st.session_state.get('validation_position_list'))
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    