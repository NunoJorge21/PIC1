import folium

# Coordenadas do centro do mapa
latitude_centro = 38.736511
longitude_centro = -9.140251


# m = folium.Map(location=[51.5074, -0.1278], zoom_start=10)
m = folium.Map(location=[38.736511, -9.140251], zoom_start=17)

# Cria um mapa
mapa = folium.Map(location=[latitude_centro, longitude_centro], zoom_start=17)

# Adiciona pontos ao mapa
coordenadas_pontos = [(40.712776, -74.005974),  # Exemplo de coordenadas (Nova Iorque)
                      (-22.9035, -43.2096)]     # Exemplo de coordenadas (Rio de Janeiro)

for coordenada in coordenadas_pontos:
    folium.Marker(coordenada).add_to(mapa)

# Salva o mapa como um arquivo HTML
mapa.save("mapa.html")
