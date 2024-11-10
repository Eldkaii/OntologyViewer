from PyQt6.QtWidgets import QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()



class ClickableFrame(QFrame):
    clicked = pyqtSignal()  # Señal emitida cuando se hace clic

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:  # Capturar el clic izquierdo
            print("Clic detectado en el ClickableFrame")  # Imprimir en consola para verificar
            self.clicked.emit()  # Emitir la señal cuando se captura el clic


