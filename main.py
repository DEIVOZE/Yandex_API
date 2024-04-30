import os
import sys
from io import BytesIO

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.uic.properties import QtCore

SCREEN_SIZE = [600, 600]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.ll1 = 37.530887
        self.ll2 = 55.703118
        self.spn = 0.002
        self.rneed = True
        self.maps = [('Схема', 'map'), ('Спутник', 'sat'), ('Гибрид', 'sat,skl')]
        self.l = 0
        self.initUI()
        self.need_point = False

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/"

        map_params = {
            "ll": f"{self.ll1},{self.ll2}",
            "spn": f"{self.spn},{self.spn}",
            "l": self.maps[self.l][1],
        }

        if self.need_point:
            map_params['pt'] = f"{self.need_point},pm2rdm"

        response = requests.get(map_request, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = BytesIO(response.content).getvalue()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.choose_map_layer = QPushButton('Схема', self)
        self.choose_map_layer.move(10, 460)
        self.choose_map_layer.resize(100, 100)
        self.choose_map_layer.clicked.connect(self.choose_layer)

        self.label = QLabel('Введите запрос для поиска', self)
        self.label.move(130, 460)
        self.label.resize(300, 30)

        self.search = QLineEdit(self)
        self.search.move(130, 490)
        self.search.resize(300, 30)

        self.search_btn = QPushButton('Искать', self)
        self.search_btn.move(130, 525)
        self.search_btn.resize(300, 35)
        self.search_btn.clicked.connect(self.get_coords)

    def paintEvent(self, event):
        try:
            if self.rneed:
                self.getImage()
                self.pixmap = QPixmap()
                self.pixmap.loadFromData(self.map_file)
                self.image.setPixmap(self.pixmap)
                self.label.setText('Введите запрос для поиска')
                self.rneed = False
        except Exception as e:
            print(e)

    def choose_layer(self):
        self.l = (self.l + 1) % 3
        self.choose_map_layer.setText(self.maps[self.l][0])
        self.rneed = True


    def keyPressEvent(self, event):
        try:
            # У меня на ноутбуке не было клавиш PageUp и PageDown, так что я вот так выкручивался
            if event.key() in (Qt.Key_Z, Qt.Key_PageUp, 1071):
                if self.spn < 5:
                    self.spn *= 2
                    self.rneed = True
            elif event.key() in (Qt.Key_X, Qt.Key_PageDown, 1063):
                if self.spn > 0.001:
                    self.spn /= 2
                    self.rneed = True
            # В PyQt если есть кнопка на форме, то стрелки почему-то не вызывают функцию,
            # так что я вместо стрелок использовал WASD
            elif event.key() in (Qt.Key_Up, 1062, Qt.Key_W):
                if self.ll2 + self.spn / 2 < 90 - self.spn // 2:
                    self.ll2 += self.spn / 2
                    self.rneed = True
            elif event.key() in (Qt.Key_Down, Qt.Key_S, 1067):
                if self.ll2 - self.spn / 2 > -90 + self.spn // 2:
                    self.ll2 -= self.spn / 2
                    self.rneed = True
            elif event.key() in (Qt.Key_Right, Qt.Key_D, 1042):
                if self.ll1 + self.spn / 2 < 180:
                    self.ll1 += self.spn / 2
                else:
                    self.ll1 = 179.99999
                self.rneed = True
            elif event.key() in (Qt.Key_Left, Qt.Key_A, 1060):
                if self.ll1 - self.spn / 2 > -180:
                    self.ll1 -= self.spn / 2
                else:
                    self.ll1 = -180
                self.rneed = True
            self.repaint()
        except Exception as e:
            print(e)


    def get_coords(self):
        geocoder_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b"
                            f"&geocode={self.search.text()}&format=json")

        # Выполняем запрос.
        try:
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                if json_response["response"]["GeoObjectCollection"]["featureMember"]:
                    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    # Полный адрес топонима:
                    toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                    # Координаты центра топонима:
                    coords = toponym["Point"]["pos"]
                    # print(f"{toponym_address} имеет координаты: {coords}")
                    self.ll1, self.ll2 = map(float, coords.split())
                    self.need_point = ','.join(coords.split())
                    self.rneed = True
                    self.repaint()
                else:
                    self.label.setText('Объект не найден')
            else:
                print("Ошибка выполнения запроса:")
                print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
