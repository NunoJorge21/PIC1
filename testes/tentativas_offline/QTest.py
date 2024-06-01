import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
import folium
from io import BytesIO

class MapaApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mapa com Pontos GPS")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.lbl_mapa = QLabel()
        self.layout.addWidget(self.lbl_mapa)

        self.lbl_latitude = QLineEdit()
        self.lbl_latitude.setPlaceholderText("Latitude")
        self.layout.addWidget(self.lbl_latitude)

        self.lbl_longitude = QLineEdit()
        self.lbl_longitude.setPlaceholderText("Longitude")
        self.layout.addWidget(self.lbl_longitude)

        self.btn_adicionar = QPushButton("Adicionar Ponto GPS")
        self.btn_adicionar.clicked.connect(self.adicionar_ponto)
        self.layout.addWidget(self.btn_adicionar)

        # Criar o mapa inicial com uma localização padrão
        self.mapa = folium.Map(location=[0, 0], zoom_start=2)
        self.atualizar_mapa()

    def adicionar_ponto(self):
        # Obter as coordenadas GPS inseridas pelo usuário
        latitude = float(self.lbl_latitude.text())
        longitude = float(self.lbl_longitude.text())
        
        # Adicionar um ponto ao mapa com as coordenadas fornecidas
        folium.Marker([latitude, longitude]).add_to(self.mapa)
        self.atualizar_mapa()

    def atualizar_mapa(self):
        # Atualizar a imagem do mapa exibida na interface
        self.lbl_mapa.setPixmap(self.pixmap_from_map(self.mapa))

    def pixmap_from_map(self, mapa):
        # Converter o mapa em uma imagem QPixmap
        img_data = BytesIO()
        mapa.save(img_data, close_file=False)
        img_data.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData
