from PyQt6 import QtWidgets, QtGui, QtCore
import os


class HelpButton(QtWidgets.QPushButton):
    def __init__(self, help_text, image_path, help_id, parent=None):
        super().__init__("?", parent)
        self.help_text = help_text
        self.image_path = image_path
        self.help_id = help_id
        self.setFixedSize(50, 50)

        # Configurar si el botón ya fue mostrado
        if self.is_help_shown():
            self.set_discreet_style()
        else:
            self.set_initial_style()
            self.start_reflection_timer()

        self.clicked.connect(self.show_help_dialog)

    def set_initial_style(self):
        self.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #4c89f7;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: #5c9aff;
            }
        """)

    def set_discreet_style(self):
        self.setVisible(False)

    def is_help_shown(self):
        path = os.path.join(os.getenv("APPDATA"),"Ontology Viewer", f"help_{self.help_id}.txt")
        return  os.path.exists(path)

    def mark_help_as_shown(self):
        file = os.path.join(os.getenv("APPDATA"),"Ontology Viewer", f"help_{self.help_id}.txt")
        with open(file, "w") as file:
            file.write("shown")

    def start_reflection_timer(self):
        # Inicializa el temporizador para crear el efecto de reflejo
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_reflection)
        self.timer.start(50)  # Actualización cada 50 ms

        # Variable para controlar el desplazamiento del reflejo
        self.reflection_position = 0

    def update_reflection(self):
        # Cambia el valor de reflection_position para mover el reflejo
        self.reflection_position += 0.05
        if self.reflection_position > 1:
            self.reflection_position = -0.3  # Reinicia la posición del reflejo

        # Aplicar el gradiente dinámico en el stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #4c89f7;
                border-radius: 25px;
                background: qlineargradient(
                    x1: {self.reflection_position - 0.3}, y1: 0, x2: {self.reflection_position + 0.3}, y2: 0,
                    stop: 0 #4c89f7, stop: 0.5 #ffffff, stop: 1 #4c89f7
                );
            }}
            QPushButton:hover {{
                background-color: #5c9aff;
            }}
        """)

    def show_help_dialog(self):
        # Detener el temporizador y el reflejo cuando se muestra el diálogo
        self.timer.stop()
        self.set_discreet_style()

        # Crear el diálogo de ayuda
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Ayuda")
        dialog.setMinimumSize(1497, 750)  # Establecer el tamaño mínimo de la ventana

        layout = QtWidgets.QVBoxLayout()

        # Imagen de ayuda
        if os.path.exists(self.image_path):
            image_label = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(self.image_path)
            # Ajustar la imagen para que ocupe todo el ancho y alto disponible en el diálogo
            pixmap = pixmap.scaled(1497, 750, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
            layout.addWidget(image_label)

        dialog.setLayout(layout)
        dialog.exec()

        # Marcar como visto y cambiar el estilo
        self.mark_help_as_shown()
