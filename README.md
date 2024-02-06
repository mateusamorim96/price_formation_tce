<details>
<summary><strong>English Version</strong></summary>

# Bid Pricing Automation Project - Open Classroom

This project was developed as part of the Open Classroom initiative, where students collaborate with professionals to solve real-world problems. It was commissioned by the State Audit Court with the aim of automating and improving the pricing formation process for public tenders.

## Problem

The challenge faced by State Audit Court employees involved efficiently determining bid prices. Manually, they had to search through historical price databases, find the desired product and its synonyms, and calculate the average value of the identified products. Inadequate pricing could result in tender failure (if the stipulated price was lower than market practice) or overpricing (if the price was significantly higher).

## Solution

The approach taken to address this issue was divided into stages:

1. **Historical Information Storage:** Elasticsearch was used to store historical information about products.

2. **ChatGPT API Integration:** The ChatGPT API was integrated to obtain synonyms for the desired product.

3. **Elasticsearch Base Search:** Based on the provided synonyms, a search was conducted in the Elasticsearch base to retrieve relevant results.

4. **Interpretation by ChatGPT:** The search results were sent to the ChatGPT API to determine which items were truly identical or similar to the target product.

5. **Interactive Table Generation:** A table with items selected by ChatGPT was implemented. This table can be modified by the user as needed.

6. **Report Generation:** A report containing pricing metrics was implemented, providing a comprehensive view of the pricing formation process.

## Current Status

The project was developed up to stage 5 but is partial. The limitation of Elasticsearch to return only 10 items is acknowledged and represents an area for contribution for future collaborators. Due to the end of the semester, the project was not completed, and we welcome contributors interested in enhancing its functionality.

## How to Contribute

If you wish to contribute to the development of this project, feel free to:

- Identify and resolve the limitation of Elasticsearch in returning items.
- Enhance the user interface in table generation and modification.
- Add additional functionalities to the pricing formation process.
- Contribute to documentation, testing, and bug fixes.

We appreciate your interest in contributing to this project!
</details>

<details>
<summary><strong>Versão em Português</strong></summary>

# Projeto de Automatização de Formação de Preços para Licitações - Sala de Aula Aberta

Este projeto foi desenvolvido como parte da iniciativa Sala de Aula Aberta, onde estudantes colaboram com profissionais para resolver problemas do mundo real. Foi encomendado pelo Tribunal de Contas do Estado, com o objetivo de automatizar e aprimorar o processo de formação de preços para abertura de licitações.

## Problema

O desafio enfrentado pelos funcionários do Tribunal de Contas do Estado consistia em realizar a formação de preços para licitações de forma eficiente. Manualmente, eles precisavam buscar em bases históricas de preços, encontrar o produto desejado e seus sinônimos, calcular o valor médio dos produtos encontrados. Uma formação de preços inadequada poderia resultar na falha da licitação (caso o preço estipulado fosse menor que o praticado no mercado) ou em superfaturamento (caso o preço fosse muito superior ao praticado).

## Solução

A abordagem adotada para resolver esse problema foi dividida em etapas:

1. **Armazenamento de Informações Históricas:** Utilizamos uma base de dados Elasticsearch para armazenar informações históricas sobre os produtos.

2. **Utilização da API do ChatGPT:** Foi integrada a API do ChatGPT para obter sinônimos do produto desejado.

3. **Busca na Base do Elastic:** A partir dos sinônimos fornecidos, realizamos uma busca na base do Elasticsearch para obter resultados relacionados.

4. **Interpretação pelo ChatGPT:** Os resultados da busca foram enviados à API do ChatGPT para determinar quais itens eram verdadeiramente iguais ou similares ao produto alvo.

5. **Geração de Tabela Interativa:** Foi implementada a geração de uma tabela com os itens selecionados pelo ChatGPT. Essa tabela pode ser modificada pelo usuário conforme necessário.

6. **Geração de Relatório:** Implementamos a geração de um relatório contendo métricas de preços, fornecendo uma visão abrangente do processo de formação de preços.

## Estado Atual

O projeto foi desenvolvido até a etapa 5, mas de forma parcial. A limitação do Elasticsearch para retornar apenas 10 itens é reconhecida e representa um ponto de contribuição para futuros colaboradores. Devido ao término do semestre, o projeto não foi concluído, e estamos abertos a colaboradores interessados em contribuir para o seu aprimoramento.

## Como Contribuir

Se você deseja contribuir para o desenvolvimento deste projeto, sinta-se à vontade para:

- Identificar e resolver a limitação do Elasticsearch para retorno de itens.
- Aprimorar a interface do usuário na geração e modificação da tabela.
- Adicionar funcionalidades adicionais ao processo de formação de preços.
- Contribuir com documentação, testes e correções de bugs.

Agradecemos antecipadamente por seu interesse em colaborar com este projeto!
</details>
