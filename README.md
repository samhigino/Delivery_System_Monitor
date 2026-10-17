# Simulação de Pesquisa de Entregadores
---
## 📋 Descrição do Problema
O objetivo deste projeto é implementar um simulador de pesquisa de entregadores de um sistema de delivery, usando a localização de bares e restaurantes de Belo Horizonte como referência. O projeto une aspectos de:

1. **Banco de Dados:** pesquisa de endereços para extração de coordenadas geográficas e utilização de DataFrames;
2. **Geometria Computacional:** implementação própria de *geohash*, projeção de coordenadas em ruas e avenidas e pesquisa por proximidade;
3. **Manipulação de Sequências:** implementação própria de uma árvore Trie compacta de prefixos.

O sistema deve permitir, em tempo razoável, ao usuário:
1. **Visualizar um mapa interativo** da cidade de Belo Horizonte e ver a localização de cada um dos bares e restaurantes que constam nos dados;
2. **Gerar entregadores** em coordenadas aleatórias, seguindo uma distruibuição normal/gaussiana em torno dos restaurantes, dividindo o total de entregadores igualmente entre cada restaurante;
3. **Pesquisar** por um restaurante específico no mapa e filtrar os entregadores por proximidade com o restaurante, destacando-os no mapa.

---

## 📂 Estrutura do projeto
```sh
├─ data/        # Guarda os dados do projeto
│ ├─ processed/ # dados gerados pelo próprio programa
│ │  ├─ cords.json
│ │  └─ new_bares.csv
│ └─ raw/       # dados brutos, pré-requisitos
│    └─ bares.csv
├─ notebooks/
│ └─ data_process.ipynb     # toda a parte relativa ao processamento de dados
├─ scripts/
│ ├─ delivery_generation.py # geração dos entregadores
│ ├─ geohash.py             # codificação e decoficação de geohash
│ ├─ trie.py                # implementação da trie e pesquisa por proximidade
│ └─ main.py                # programa principal
└─ requirements.txt # Pré-requisitos de python para executar o programa
```

---

## ▶️ Instruções de Execução

O programa foi testado para Python 3.13.15. Não podemos garantir que a execução será exata em outras versões.

1. **Pré-requisitos**
    - Instale todas as bibliotecas especificadas em requirements.txt abrindo o prompt de comando e digitando ```pip install -r``` 

2. **Processamento de Dados**
(Recomendamos pular esta parte e usar os dados que já estão disponibilizados no repositório. Mas caso seja de interesse do usuário obter os dados processados a partir dos dados brutos, siga os passos abaixo.)
    - Apague todos os arquivos dentro de ```data/processed/```;
    - Acesse o notebook em ```notebooks/data_process.ipynb```;
    - Execute as células uma a uma, em ordem - se desejar, confira a saída de cada uma para ver os passos intermediários;
    - Confira se todos os arquivos foram gerados em ```data/processed/``` corretamente. A execução pode levar um tempo.

3. **Execução principal**
    - Execute o script ```scripts/main.py```;
