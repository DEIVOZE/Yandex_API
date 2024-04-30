import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
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

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/"

        map_params = {
            "ll": f"{self.ll1},{self.ll2}",
            "spn": f"{self.spn},{self.spn}",
            "l": self.maps[self.l][1]
        }

        response = requests.get(map_request, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

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

    def paintEvent(self, event):
        if self.rneed:
            self.getImage()
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.rneed = False

    def choose_layer(self):
        self.l = (self.l + 1) % 3
        self.choose_map_layer.setText(self.maps[self.l][0])
        self.rneed = True

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        # У меня на ноутбуке не было клавиш PageUp и PageDown, так что я вот так выкручивался
        if event.key() in (Qt.Key_Z, Qt.Key_PageUp):
            if self.spn < 5:
                self.spn *= 2
                self.rneed = True
        elif event.key() in (Qt.Key_X, Qt.Key_PageUp):
            if self.spn > 0.001:
                self.spn /= 2
                self.rneed = True
        # В PyQt если есть кнопка на форме, то стрелки почему-то не вызывают функцию,
        # так что я вместо стрелок использовал WASD
        elif event.key() in (Qt.Key_Up, Qt.Key_W):
            if self.ll2 + self.spn / 2 < 90 - self.spn // 2:
                self.ll2 += self.spn / 2
                self.rneed = True
        elif event.key() in (Qt.Key_Down, Qt.Key_S):
            if self.ll2 - self.spn / 2 > -90 + self.spn // 2:
                self.ll2 -= self.spn / 2
                self.rneed = True
        elif event.key() in (Qt.Key_Right, Qt.Key_D):
            if self.ll1 + self.spn / 2 < 180:
                self.ll1 += self.spn / 2
            else:
                self.ll1 = 179.99999
            self.rneed = True
        elif event.key() in (Qt.Key_Left, Qt.Key_A):
            if self.ll1 - self.spn / 2 > -180:
                self.ll1 -= self.spn / 2
            else:
                self.ll1 = -180
            self.rneed = True
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
