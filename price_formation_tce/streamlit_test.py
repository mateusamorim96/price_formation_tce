from dotenv import load_dotenv
import os

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import streamlit as st

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ['gpt_api_key']

template_similar_words = """Desejo comprar um material e gostaria de buscar por diferentes variações no nome desse material para amplificar o sucesso de encontrar muitos resultados.
Por exemplo, eu desejo comprar uma calculadora e te faço o seguinte pedido: Gostaria de sinônimos para a palavra 'caneta esferográfica', separados por vírgula. 
O que eu espero como resposta: caneta esferográfica, tinteiro, caneta de ponta fina, caneta nanquim, caneta hidrográfica. 
O que eu não espero como resposta: lápis, lapiseira, pincel, marca texto.
Dessa forma, eu gostaria de sinônimos para a palavra '{desirable_item}', separados por vígula."""

def print_item_field(item, item_suggestions):
    global similar_words_dropdown
    print("Chamando pelo botão")
    suggestions = item_suggestions.run(item)
    print(suggestions)
    similar_words_lst = suggestions.strip().split(',')
    st.session_state["similar_words_lst_options"] = similar_words_lst
    
def get_llm(temperature):
    
    return OpenAI(temperature=temperature)

st.title("TCE Price Formation")

if "similar_words_lst_options" not in st.session_state:
    st.session_state["similar_words_lst_options"] = []

desirable_item = st.sidebar.text_input("Item desejado")
temperature_slider = st.sidebar.slider("Criatividade", 0, 100, 60, 5)

llm = get_llm(temperature_slider / 100)
prompt_suggestion_names = PromptTemplate(input_variables = ['desirable_item'], template = template_similar_words)
item_suggestions = LLMChain(llm=llm, prompt=prompt_suggestion_names, output_key="suggestions")

search_button = st.sidebar.button("Pesquisar", on_click=print_item_field, kwargs={"item": desirable_item, "item_suggestions": item_suggestions})

similar_words_dropdown = st.sidebar.multiselect("Termos associados", options=st.session_state.similar_words_lst_options, key='suggestion_dropdown')

