import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.ll1 = 37.530887
        self.ll2 = 55.70311
        self.spn = 0.002
        self.rneed = True
        self.initUI()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.ll1},{self.ll2}&spn={self.spn},{self.spn}&l=map"
        response = requests.get(map_request)

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

    def paintEvent(self, event):
        if self.rneed:
            self.getImage()
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)
            self.rneed = False

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.spn += 0.01
            self.rneed = True
        elif event.key() == Qt.Key_PageDown:
            self.spn -= 0.01
            self.rneed = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())