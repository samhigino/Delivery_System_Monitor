import dash
import pandas as pd
import osmnx as ox
import plotly.express as px
import plotly.graph_objects as go
import delivery_generation as dg
import numpy as np
from dash import Input, Output, State, dcc, html
from shapely.geometry import Point
from math import radians, sin, cos, sqrt, atan2
from pyproj import Transformer

#+#=#+#=#+#=#+#=#+#
#+#=#  MALHA  #+#=# 
#+#=#+#=#+#=#+#=#+#
#Grafo de ruas para spawnar os entregadores no local apropriado
lugar = "Belo Horizonte, Minas Gerais, Brazil"
grafo = ox.graph_from_place(lugar, network_type="drive")

#Prepara a malha so uma vez
grafo_proj = ox.project_graph(grafo)
_, arestas_gdf = ox.graph_to_gdfs(grafo_proj)

# Conversor Lat/Lon -> Cordenada no grafo
transformer = Transformer.from_crs( "EPSG:4326", # Sistema de cordeenadas com lat/lon em graus
    grafo_proj.graph["crs"],
    always_xy=True
)
# Conversor Cordenada no grafo -> Lat/Lon
transformer_inverso = Transformer.from_crs(grafo_proj.graph["crs"], "EPSG:4326", always_xy=True)

#+#=#+#=#+#=#+#=#+#
#+#=#  DADOS  #+#=# 
#+#=#+#=#+#=#+#=#+#
#Lê a tabela de dados dos restaurantes e faz o pré-processamento
tabela_restaurantes = pd.read_csv("data/processed/new_bares.csv", sep=",")
#Tira a coluna de indice antiga
tabela_restaurantes = tabela_restaurantes.drop(
    columns=["old_index"]
)
#Cria novos indices
tabela_restaurantes = tabela_restaurantes.reset_index(drop=True)

#Tira números presentes no inicio de alguns nomes de restaurantes, provavelmente algum cpf ou outro documento relacionado
#Primeiro uma sequencia de numeros seguindo o padrão xx.xxx.xxx q aparecia no inicio e uma de 11 números q aparecia no fim 
tabela_restaurantes["NOME"] = tabela_restaurantes["NOME"].str.replace(r"^\s*\d{2}\.\d{3}\.\d{3}\s*", "", regex=True).replace(r"\d{11}","",regex=True)
tabela_restaurantes["NOME_FANTASIA"] = tabela_restaurantes["NOME_FANTASIA"].str.replace(r"^\s*\d{2}\.\d{3}\.\d{3}\s*", "", regex=True).replace(r"\d{11}","", regex=True) 
#Tanto do nome como nome_fantasia

#Configura uma coluna para ser o display do nome do restaurante
tabela_restaurantes["NOME_FANTASIA_DISPLAY"] = tabela_restaurantes["NOME_FANTASIA"].fillna(tabela_restaurantes["NOME"])

#+#=#+#=#+#=#+#=#+#
#+#=## LAYOUT #+#=#
#+#=#+#=#+#=#+#=#+#
aplicativo = dash.Dash(__name__)

#Cor do topo da interface
cor_cima = "#F39090"

#Layout do site em HTML
aplicativo.layout = html.Div(
    children=[
        dcc.Store(
            id="entregadores_store",
            data=[]
        ),
        html.Div([
            html.H2("",style={
                "marginTop": "0px",
                "marginBottom": "0px", 
                "backgroundColor": cor_cima,
                "height": "10px",
            }),
            html.H1("INTERFACE DE ENTREGAS",
                    style={
                        "textAlign": "center", 
                        "fontFamily": "Andale Mono, monospace",  
                        "fontSize": "64px",  
                        "color": "#FFF8F8",  
                        "marginTop": "0px",
                        "marginBottom": "15px", 
                        "backgroundColor": cor_cima,
                        "height": "64px",
                        "display": "flex",
                        "justifyContent": "center",
                        "-webkit-text-stroke": "1.7px black",
                    },
            ),
            html.Hr(style={
                "borderColor": "#49111C",
                "marginTop": "0px",
                "marginBottom": "0px", 
                "borderWidth": "2px",
                "width": "100%",
                "margin": "0px",
            })],style={
                "width": "100%",
                "backgroundColor": cor_cima,
            }
        ),
        html.Div(
            children=[
                dcc.Input(id = "n_entregadores",
                        placeholder="Digite a quantidade de entregadores", 
                        type="number",
                        min=0,
                        max=2000,
                        step=1,
                        style={
                            "width": "400px",
                            "height": "40px",    
                            "padding": "10px",
                            "marginTop": "45px",
                }),
                html.Button("Atualizar Mapa", id="atualizar-mapa", n_clicks=0, style={
                    "backgroundColor": "#49111C",
                    "fontWeight": "bold",
                    "color": "#F2F4F3",
                    "border": "none",
                    "padding": "10px 20px",
                    "fontSize": "16px",
                    "cursor": "pointer",
                    "height": "40px",  
                    "width": "200px",
                    "marginTop": "45px",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
                })
            ],
            style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "height": "85px",
                    "backgroundColor": "#F2F4F3",
                    "gap": "20px",
                    "width": "100%",
            }
        ),
        html.Div([
            html.Div([
                html.Label(
                    "Distância máxima do entregador em Km",
                    style={
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "color": "#333",
                        "marginBottom": "15px",
                        "display": "block"
                    }
                ),

                dcc.Slider(
                    id="n_km_max",
                    min=1,
                    max=15,
                    step=1,
                    value=2,
                    marks={
                        1: "1 km",
                        5: "5 km",
                        10: "10 km",
                        15: "15 km"
                    },
                    tooltip={
                        "placement": "bottom",
                        "always_visible": True
                    },
                    included=True
                )
            ], style={
                "width": "65%",
                "marginTop": "10px",
                "padding": "15px",
                "backgroundColor": "#f8f9fa",
                "borderRadius": "10px",
                "boxShadow": "0 3px 7px rgba(0,0,0,0.1)"
            }),
            dcc.Dropdown(
                id="dropdown_restaurantes",
                options=[],
                placeholder="Digite o nome do restaurante...",
                searchable=True,
                clearable=True,
                optionHeight=40,
                style={
                    "width": "400px",
                    "marginTop": "8px",
                    "zIndex": 1000,
                }
            )],style={
                "display": "flex",
                "flexDirection": "row",
                "alignItems": "center",
                "justifyContent": "center",
                "width": "100%",
                "backgroundColor": "#F2F4F3",
                "gap": "20px",
            }
        ),
        html.Div(
            dcc.Graph(
                id="mapa_entrega",
                style={
                    "width": "100%",
                    "marginTop": "20px",
                    "height": "600px",
                    "border": "2px solid #49111C",
                    "borderRadius": "8px",
                    "overflow": "hidden",
                },
            ),
            style={
                "display": "flex",
                "height": "620px",
                "width": "90%",
                "justifyContent": "center",
                "alignItems": "center",
                "backgroundColor": "#F2F4F3",
            },
        ),
    ],
    style={
        "backgroundColor": "#F2F4F3",
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "margin": "0px",
        "padding": "0px",
        "width": "100vw",       
        "height": "100vh",    
        "position": "absolute",  
        "top": "0px",
        "left": "0px",
        "overflow": "hidden",
    }
)

#+#=#+#=#+#=#+#=#+#
#+#=## LÓGICA #+#=#
#+#=#+#=#+#=#+#=#+#
def distancia_km(latitude_p, longitude_p, latitude_s, longitude_s):   #Calculo da distancia em km pela latitude/longitude
    raio_total = 6371
    latitude_p = radians(latitude_p)
    longitude_p = radians(longitude_p)
    latitude_s = radians(latitude_s)
    longitude_s = radians(longitude_s)

    deltalat = latitude_s - latitude_p
    deltalon = longitude_s - longitude_p
    qtroçoéesse = (sin(deltalat / 2) ** 2 + cos(latitude_p) * cos(latitude_s) * sin(deltalon / 2) ** 2) #Formula que calcula a distancia entre dois pontos no globo, n tenho a MINIMA ideia como funfa so aceitei
    return 2 * raio_total * atan2(sqrt(qtroçoéesse), sqrt(1 - qtroçoéesse)) #Coitado de qm teve q pensar isso pela primeira vez

#Função básica que atualiza o mapa de acordo com os estados das estruturas do html
def atualizar_o_mapa(n_clicks, entregadores, filtro, restaurante_id):
    #Zoom maior se tiver vendo um restaurante especifico ou toda bh
    if restaurante_id is not None:
        zom = 14
    else:
        zom = 12

    #
    fig = px.scatter_map(
        tabela_restaurantes,
        lat="LATITUDE",
        lon="LONGITUDE",
        hover_name="NOME_FANTASIA_DISPLAY",
        height=600,
        #width = 1725,
        zoom=zom,
        color_discrete_sequence=["#A0A0A0"],
    )

    # Deixa o resto opaco
    fig.update_traces(
        marker={
            "size": 8,
            "opacity": 0.35,
        }
    )

    # Define o centro padrão 
    centro = {
        "lat": -19.917,
        "lon": -43.945,
    }

    # Highlight
    if restaurante_id is not None:
        restaurante = tabela_restaurantes.loc[restaurante_id]
        lat = float(restaurante["LATITUDE"])
        lon = float(restaurante["LONGITUDE"])

        #Define o centro no restaurante selecionado no Dropdown 
        centro = {
            "lat": lat,
            "lon": lon,
        }

        #Põe o restaurante selecionado em destaque no mapa com simbolozinho de restauraante emoji
        fig.add_trace(
            go.Scattermap(
                lat=[lat],
                lon=[lon],
                mode="text",
                text=["🍽️"],
                textfont={
                    "size": 30,
                    "color": "#E63946",
                },
                name="Restaurante selecionado",
                showlegend=False,
                customdata=[[restaurante["NOME_FANTASIA_DISPLAY"], lat, lon]],
                hovertemplate=(
                    "%{customdata[0]}<br>"
                    "LATITUDE: %{customdata[1]}<br>"
                    "LONGITUDE: %{customdata[2]}"
                    "<extra></extra>"
                ),
            )
        )

        # Desenha o círculo do restaurante selecionado
        if filtro is not None:
            angulos = np.linspace(0, 2 * np.pi, 100)

            lat_rad = np.radians(lat)
            lon_rad = np.radians(lon)
            distancia = float(filtro) / 6371

            lat_circulo = np.arcsin(np.sin(lat_rad) * np.cos(distancia)+ np.cos(lat_rad) * np.sin(distancia) * np.cos(angulos))

            lon_circulo = lon_rad + np.arctan2(np.sin(angulos) * np.sin(distancia) * np.cos(lat_rad), np.cos(distancia)- np.sin(lat_rad) * np.sin(lat_circulo))
            #Conecta os pontos em um poligono, que fica um circulo aproximada pq sao 100 pontos ao redor do raio
            fig.add_trace(
                go.Scattermap(
                    lat=np.degrees(lat_circulo),
                    lon=np.degrees(lon_circulo),
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba(230, 57, 70, 0.15)",
                    line={
                        "color": "#E63946",
                        "width": 2,
                    },
                    name=f"Raio de {filtro} km",
                    hoverinfo="skip",
                )
            )

    # Separa os entregadores dentro e fora do raio
    if entregadores:
        locais = np.array(entregadores, dtype=float)

        latitudes = locais[:, 0]
        longitudes = locais[:, 1]

        dentro = np.zeros(len(locais), dtype=bool)

        # SUBSTITUIR AQUI PELO GEOHASH TODo, POR ENQUANTO TA USANDO ALGO INEFICIENTE
        if restaurante_id is not None and filtro is not None:
            lat_rest = float(centro["lat"])
            lon_rest = float(centro["lon"])

            for i, (lat_ent, lon_ent) in enumerate(locais):
                distancia = distancia_km(lat_rest, lon_rest,lat_ent,lon_ent)
                dentro[i] = distancia <= float(filtro)

        # Entregadores fora do círculo ficam azul claro e transparentes
        fora = ~dentro

        if np.any(fora):
                fig.add_trace(
                    go.Scattermap(
                        lat=latitudes[fora],
                        lon=longitudes[fora],
                        mode="markers",
                        marker={
                            "size": 13,
                            "color": "#00A6FB",
                            "opacity": 0.85,
                        },
                        name="Entregadores fora do raio",
                        customdata=np.column_stack((
                            latitudes[fora],
                            longitudes[fora],
                        )),
                        hovertemplate=(
                            "Entregador fora do raio<br>"
                            "Latitude: %{customdata[0]:.5f}<br>"
                            "Longitude: %{customdata[1]:.5f}"
                            "<extra></extra>"
                        ),
                    )
                )

        # Entregadores dentro do círculo ficam azul escuro e menso trans
        if np.any(dentro):
            fig.add_trace(
                go.Scattermap(
                    lat=latitudes[dentro],
                    lon=longitudes[dentro],
                    mode="markers",
                    marker={
                        "size": 15,
                        "color": "#003B73",
                        "opacity": 0.95,
                    },
                    name="Entregadores dentro do raio",
                    customdata=np.column_stack((
                        latitudes[dentro],
                        longitudes[dentro],
                    )),
                    hovertemplate=(
                        "Entregador dentro do raio<br>"
                        "Latitude: %{customdata[0]:.5f}<br>"
                        "Longitude: %{customdata[1]:.5f}"
                        "<extra></extra>"
                    ),
                )
            )

    #Carrega o mapa
    fig.update_layout(
        map_style="carto-positron",
        map_center=centro,
        autosize=True,
        showlegend=False,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    return fig

def projetar_entregadores_nas_ruas(grafo, entregadores):
    pontos = np.asarray(entregadores, dtype=float)

    if pontos.size == 0:
        return []

    latitudes = pontos[:, 0]
    longitudes = pontos[:, 1]

    # Converte todas as coordenadas para km
    xs, ys = transformer.transform(longitudes, latitudes)

    # Busca a parte mais proxima de uma vez, demora MUIIITO tempo, pq tem mt rua em BH :')
    arestas = ox.distance.nearest_edges(grafo_proj,X=xs,Y=ys,)

    pontos_projetados = []

    # ajusta cada ponto pra projetar na rua correspondente
    for x, y, aresta in zip(xs, ys, arestas):
        geometria = arestas_gdf.loc[tuple(aresta), "geometry"]

        ponto = Point(x, y)
        ponto_rua = geometria.interpolate(geometria.project(ponto) )
        lon, lat = transformer_inverso.transform(ponto_rua.x,ponto_rua.y,)
        pontos_projetados.append([lat, lon])

    return pontos_projetados


#+#=#+#=#+#=#+#=#+#=#+#
#+#=## CALLBACKS #+#=#=
#+#=#+#=#+#=#+#=#+#=#+#
#Callback que gera os entregadores e guarda no store se clicar no botão de atualizar mapa
@aplicativo.callback(
    Output("entregadores_store", "data"),
    Input("atualizar-mapa", "n_clicks"),
    State("n_entregadores", "value"),
    State("dropdown_restaurantes", "value"),
)
def gerar_entregadores(n_clicks, n_entregadores, restaurante_id):
    if not n_clicks:
        return []

    if (n_entregadores is None or not 0 <= n_entregadores <= 50000):
        return dash.no_update

    # Escolhe restaurantes aleatórios como pontos de partida
    restaurantes_validos = tabela_restaurantes.dropna(subset=["LATITUDE", "LONGITUDE"])
    restaurantes_validos = restaurantes_validos[restaurantes_validos["LATITUDE"].between(-90, 90) & restaurantes_validos["LONGITUDE"].between(-180, 180)]

    if restaurantes_validos.empty and n_entregadores > 0:
        return dash.no_update

    # Cada entregador é associado a um restaurante aleatório
    escolhidos = restaurantes_validos.sample(
        n=int(n_entregadores),
        replace=True,
    )

    locais = []
    # Gera entregadores ao reedor dos restaurantes de acordo com a normal
    for _, restaurante in escolhidos.iterrows():
        entregadores = dg.generate_delivery_single(
            lat=restaurante["LATITUDE"],
            lon=restaurante["LONGITUDE"],
            n=1,
            desv=0.001
        )
        locais.append(entregadores[0].tolist())

    return projetar_entregadores_nas_ruas(grafo, locais)

#Callback que atualiza o mapa quando gera entregadores ou qnd muda o filtro de dist/restaurante q ta no dropdown
@aplicativo.callback(
    Output("mapa_entrega", "figure"),
    Input("entregadores_store", "data"),
    Input("dropdown_restaurantes", "value"),
    Input("n_km_max", "value"),
)
def atualizar_mapa(entregadores, restaurante_id, filtro):
    return atualizar_o_mapa(
        0,
        entregadores,
        filtro,
        restaurante_id,
 )

#Callback que busca restaurantes pesquisa a pesquisa pra n engasgar com >>>>20K de linhas<<<<< de restaurantes
@aplicativo.callback(
    Output("dropdown_restaurantes", "options"),
    Input("dropdown_restaurantes", "search_value"),
    State("dropdown_restaurantes", "value"),
)
def buscar_restaurantes(texto, restaurante_atual):
    opcoes = []

    # Mantem o restaurante atualmente selecionado
    if restaurante_atual is not None:
        selecionado = tabela_restaurantes.loc[restaurante_atual]

        opcoes.append({
            "label": str(selecionado["NOME_FANTASIA_DISPLAY"]),
            "value": int(restaurante_atual),
        })

    # Só pesquisa quando ter 2 caracter ou mais
    if texto and len(texto.strip()) >= 2:
        busca = texto.strip()
        encontrados = tabela_restaurantes[tabela_restaurantes["NOME_FANTASIA_DISPLAY"].str.contains(busca, case=False, na=False, regex=False)].head(50)

        for i, linha in encontrados.iterrows():
            if i != restaurante_atual: #pra n repetir
                opcoes.append({
                    "label": str(linha["NOME_FANTASIA_DISPLAY"]),
                    "value": int(i),
                })

    return opcoes

if __name__ == "__main__":
    aplicativo.run(debug=True)