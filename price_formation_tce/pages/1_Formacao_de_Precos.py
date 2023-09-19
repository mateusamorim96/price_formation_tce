from dotenv import load_dotenv
import os

from elasticsearch import Elasticsearch

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import streamlit as st

st.set_page_config(page_title="Formação de Preços", page_icon="💲")

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ['gpt_api_key']

template_similar_words = """Desejo comprar um material e gostaria de buscar por diferentes variações no nome desse material para amplificar o sucesso de encontrar muitos resultados.
Por exemplo, eu desejo comprar uma calculadora e te faço o seguinte pedido: Gostaria de sinônimos para a palavra 'caneta esferográfica', separados por vírgula. 
O que eu espero como resposta: caneta esferográfica, tinteiro, caneta de ponta fina, caneta nanquim, caneta hidrográfica. 
O que eu não espero como resposta: lápis, lapiseira, pincel, marca texto.
Dessa forma, eu gostaria de sinônimos para a palavra '{desirable_item}', separados por vígula."""

@st.cache_resource
def elastic_connection(url: str) -> Elasticsearch:
    es = Elasticsearch(hosts=url)
    
    return es

@st.cache_data
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
    
    string_query = " ".join(f"({item.strip()})" for item in query_items)
    
    resp = es.search(index=indice, body={
    "query": {
        "query_string": {
        "query": string_query,
        "default_field": field
        }
    },
    "track_total_hits": True
    })
    
    return 

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
temperature_slider = st.sidebar.slider("Criatividade", 0, 100, 60, 5, help="Quanto maior a criatividade, maior o risco que o GPT assume de errar.")

llm = get_llm(temperature_slider / 100)
prompt_suggestion_names = PromptTemplate(input_variables = ['desirable_item'], template = template_similar_words)
item_suggestions = LLMChain(llm=llm, prompt=prompt_suggestion_names, output_key="suggestions")

btn_search_related_words = st.sidebar.button("Pesquisar", on_click=print_item_field, kwargs={"item": desirable_item, "item_suggestions": item_suggestions, "elastic_url": elastic_url})

similar_words_dropdown = st.sidebar.multiselect("Termos associados", options=st.session_state.similar_words_lst_options, key='suggestion_dropdown')

if "indices_elastic_list_options_page1" not in st.session_state:
    st.session_state["indices_elastic_list_options_page1"] = []
    
if "elastic_indices_field_list_options" not in st.session_state:
    st.session_state["elastic_indices_field_list_options"] = []
    
indice_name = st.sidebar.selectbox("Carregar campos do indice:", options=st.session_state.indices_elastic_list_options_page1, key='index_dropdown', help='Selecione o indice que deseja realizar a busca.')
load_fields_from_indices(elastic_url, indice_name)

selected_field = st.sidebar.selectbox("Selecione um campo:", options=st.session_state.elastic_indices_field_list_options, help='Selecione o campo que contém a informação de interesse.')

btn_load_from_elastic = st.sidebar.button("Consultar base de dados")