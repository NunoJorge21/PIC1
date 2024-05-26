import tkinter as tk
import webbrowser
import folium

def abrir_mapa():
    webbrowser.open_new("mapa.html")

def adicionar_ponto():
    # Obter as coordenadas GPS inseridas pelo usuário
    latitude = float(entrada_latitude.get())
    longitude = float(entrada_longitude.get())
    
    # Adicionar um ponto ao mapa com as coordenadas fornecidas
    folium.Marker([latitude, longitude]).add_to(m)

    # Salvar o mapa atualizado como um arquivo HTML temporário
    m.save("mapa_temp.html")

    # Abrir o mapa atualizado em um navegador web externo
    abrir_mapa()

# Criar a janela principal
root = tk.Tk()
root.title("Mapa com Pontos GPS")

# Criar um mapa inicial com uma localização padrão
m = folium.Map(location=[0, 0], zoom_start=2)

# Entradas para as coordenadas GPS
lbl_latitude = tk.Label(root, text="Latitude:")
lbl_latitude.pack()
entrada_latitude = tk.Entry(root)
entrada_latitude.pack()

lbl_longitude = tk.Label(root, text="Longitude:")
lbl_longitude.pack()
entrada_longitude = tk.Entry(root)
entrada_longitude.pack()

# Botão para adicionar ponto GPS
botao_adicionar = tk.Button(root, text="Adicionar Ponto GPS", command=adicionar_ponto)
botao_adicionar.pack()

# Executar o loop principal da aplicação
root.mainloop()


