import rdflib
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView,QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QUrl

import main
from ontology_loader_v6 import OntologyLoader
from clickable_widgets_v6 import ClickableFrame
from carga_xcel import *
from help import HelpButton

import sys
import json  # Añadir esta línea al inicio para cargar JSON
import csv
import re
from help import *
import os

import logging

# 1. Generar la ruta para el archivo de log en %APPDATA%
log_path = os.path.join(os.getenv("APPDATA"), "Ontology Viewer", "log.txt")

# 2. Crear el directorio si no existe
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# 3. Configurar logging para usar la nueva ubicación del archivo
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class OntologyViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(OntologyViewer, self).__init__()

        self.loader = OntologyLoader()  # Instancia del nuevo manejador de ontologías
        self.version = 'beta'
        self.file_path = ''

        self.update_window_title(None)

        self.setGeometry(100, 100, 1200, 600)
        self.graph = rdflib.Graph()  # Grafo RDF
        self.is_all_sections_active = True
        self.is_secondary_sections_active = True
        self.is_third_sections_active = True
        self.ontology_file = ""
        self.is_maximized = False

        # Inicializamos tecnica_buttons como un diccionario vacío
        self.tecnica_buttons = {}

        # Crear el área de desplazamiento (scroll area)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        # Personalizar la barra de desplazamiento
        self.scroll_area.setStyleSheet("""
                   QScrollBar:vertical {
                       background-color: #f0f0f0;    /* Color de fondo de la barra de scroll */
                       width: 25px;                   /* Ancho de la barra */
                       margin: 15px 3px 15px 3px;     /* Márgenes superior, derecho, inferior, izquierdo */
                       border-radius: 5px;            /* Bordes redondeados */
                   }
                   QScrollBar::handle:vertical {
                       background-color: #3d52a0;     /* Color de la "manija" que se arrastra */
                       min-height: 30px;              /* Altura mínima de la manija */
                       border-radius: 5px;
                   }
                   QScrollBar::handle:vertical:hover {
                       background-color: #7091e6;     /* Color de la manija al pasar el mouse */
                   }
                   QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                       background: none;              /* Quita las flechas al final de la barra */
                   }
                   QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                       background: none;              /* Quita el espacio entre el fondo y la manija */
                   }
               """)

        # Crear un widget central que contendrá todo el contenido
        self.central_widget = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.central_widget)
        self.is_highlighted = False  # Estado inicial

        # Establecer el layout principal
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Establecer el layout principal del scroll_area como layout central de la ventana
        self.setCentralWidget(self.scroll_area)

        # Aplicar estilos generales
        self.setStyleSheet("""
            QWidget { background-color: #ede8f5; color: black; }
            QPushButton {
                background-color: #3d52a0; color: black;
                border-radius: 8px; padding: 10px;
                border: 1px solid black;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2d42a0; }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: black;
            }
            QScrollArea { border: none; }
        """)

        # Título de la aplicación
        self.title_label = QtWidgets.QLabel("Proyectos de Investigación", self)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px; font-weight: bold;
            color: black; font-family: 'Segoe UI', Arial, sans-serif;
            color-background: 
        """)
        # Configurar el efecto de sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)  # Radio de difuminado de la sombra
        shadow.setXOffset(4)  # Desplazamiento horizontal de la sombra
        shadow.setYOffset(4)  # Desplazamiento vertical de la sombra
        shadow.setColor(QColor(0, 0, 0, 160))  # Color de la sombra con transparencia

        # Aplicar el efecto de sombra al QLabel
        self.title_label.setGraphicsEffect(shadow)

        self.main_layout.addWidget(self.title_label)

        # Crear botones de ayuda con diferentes textos e imágenes


        self.button_help_init = HelpButton("", "help_images/1_menu_inicio.png", "init_help", self)

        # Agregar botones al layout
        self.main_layout.addWidget(self.button_help_init, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


        self.first_time_label = QtWidgets.QLabel(
            " <img src='icons/arrow_up.png' width='16' height='16' /> <br>  💡  ¿Primera vez? 💡  ", self)
        self.first_time_label.hide()

        self.first_time_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: black;
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                font-weight: 500;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.first_time_label.setFixedSize(200, 60)

        # Configurar el efecto de sombra
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 160))
        self.first_time_label.setGraphicsEffect(self.shadow_effect)

        # Variables para el movimiento de la sombra
        self.shadow_offset_x = 2
        self.shadow_offset_y = 2
        self.shadow_direction_x = 1
        self.shadow_direction_y = 1

        if not os.path.exists("help_init_help.txt"):
            self.first_time_label.show()
        self.main_layout.addWidget(self.first_time_label,alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Espacio en blanco para desplazar el botón hacia abajo
        self.spacerInit = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Policy.Minimum,
                                                QtWidgets.QSizePolicy.Policy.Minimum)
        self.main_layout.addItem(self.spacerInit)

        # Botón para cargar la ontología
        self.load_button = QtWidgets.QPushButton('Cargar repositorio', self)
        self.load_button.setFixedSize(200, 50)
        self.load_button.clicked.connect(self.load_ontology)
        self.main_layout.addWidget(self.load_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)




        # BOTONES DE INFERENCIA
        # Crear el botón para mostrar/ocultar el recuadro de configuración avanzada
        self.advanced_settings_button = QtWidgets.QPushButton("Configuración avanzada")
        self.advanced_settings_button.setIcon(QtGui.QIcon('icons/advance_configuracion.png'))
        self.advanced_settings_button.setCheckable(True)  # Permite que el botón mantenga su estado (presionado o no)

        self.advanced_settings_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: #4c89f7;
                background-color: transparent;
                border: none;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #6a9ef7;
            }
        """)
        self.advanced_settings_button.clicked.connect(self.toggle_advanced_settings)

        self.cargar_con_excel = QtWidgets.QPushButton("Cargar con excel")
        self.cargar_con_excel.setIcon(QtGui.QIcon('icons/advance_configuracion.png'))
        self.cargar_con_excel.setStyleSheet("""
                    QPushButton {
                        font-size: 12px;
                        color: #4c89f7;
                        background-color: transparent;
                        border: none;
                        text-decoration: underline;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        color: #6a9ef7;
                    }
                """)
        self.cargar_con_excel.clicked.connect(lambda: load_excel_and_populate_ontology(self))

        # Crear el contenedor y aplicar estilo
        self.checkbox_container = QtWidgets.QGroupBox()
        self.checkbox_container.setVisible(False)  # Ocultar el recuadro al inicio
        self.checkbox_container_layout = QtWidgets.QVBoxLayout(self.checkbox_container)

        # Crear un layout horizontal para el título y el botón de ayuda
        title_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Opciones de Inferencia")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")

        # Crear botón de ayuda
        self.help_button = QtWidgets.QPushButton("?")
        self.help_button.setFixedSize(20, 20)
        self.help_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: white;
                background-color: #4c89f7;
                border-radius: 10px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #5c9aff;
            }
        """)
        self.help_button.clicked.connect(self.show_help_dialog)

        # Agregar el título y botón de ayuda al layout del título
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.help_button)
        title_layout.addStretch()

        # Agregar el layout del título al layout principal del contenedor
        self.checkbox_container_layout.addLayout(title_layout)

        # Crear un QGridLayout para organizar los checkboxes en varias filas y columnas
        self.checkbox_layout = QtWidgets.QGridLayout()
        self.checkbox_layout.setContentsMargins(10, 10, 10, 10)  # Ajustar márgenes

        # Crear los checkboxes individuales
        self.replaceFile_checkbox = QtWidgets.QCheckBox("Reemplazar Archivo")
        self.classAssertions_checkbox = QtWidgets.QCheckBox("Class Assertions")
        self.classAssertions_checkbox.setChecked(True)  # Marcar este checkbox por defecto
        self.propertyAssertions_checkbox = QtWidgets.QCheckBox("Property Assertions")
        self.propertyAssertions_checkbox.setChecked(True)  # Marcar este checkbox por defecto
        self.subClass_checkbox = QtWidgets.QCheckBox("Subclass")
        self.equivalentClass_checkbox = QtWidgets.QCheckBox("Equivalent Class")
        self.disjointClasses_checkbox = QtWidgets.QCheckBox("Disjoint Classes")
        self.equivalentObjectProperty_checkbox = QtWidgets.QCheckBox("Equivalent Object Property")
        self.objectPropertyCharacteristic_checkbox = QtWidgets.QCheckBox("Object Property Characteristic")
        self.inverseObjectProperties_checkbox = QtWidgets.QCheckBox("Inverse Object Properties")
        self.subObjectProperty_checkbox = QtWidgets.QCheckBox("Sub Object Property")
        self.dataPropertyCharacteristic_checkbox = QtWidgets.QCheckBox("Data Property Characteristic")
        self.justLoadNoInference = QtWidgets.QCheckBox("Cargar Sin Inferencia")

        # Lista de checkboxes y posición en una cuadrícula de tres columnas
        checkboxes = [
            (self.replaceFile_checkbox, 0, 0),
            (self.classAssertions_checkbox, 0, 1),
            (self.subClass_checkbox, 0, 2),
            (self.propertyAssertions_checkbox, 1, 0),
            (self.disjointClasses_checkbox, 1, 1),
            (self.equivalentObjectProperty_checkbox, 1, 2),
            (self.objectPropertyCharacteristic_checkbox, 2, 0),
            (self.inverseObjectProperties_checkbox, 2, 1),
            (self.subObjectProperty_checkbox, 2, 2),
            (self.dataPropertyCharacteristic_checkbox, 3, 0),
            (self.equivalentClass_checkbox, 3, 1),
            (self.justLoadNoInference, 3, 2)
        ]

        # Estilo individual para cada checkbox
        for checkbox, row, col in checkboxes:
            if row + col == 0:
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 14px;
                        color: #333;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        padding: 5px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 3px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #b85252;
                        border: 1px solid #b85252;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: #c0c0c0;
                        border: 1px solid #a0a0a0;
                    }
                """)
            elif row + col == 5:
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 14px;
                        color: #333;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        padding: 5px;
                    }
                    QCheckBox::indicator {
                        width: 18px;
                        height: 18px;
                        border-radius: 3px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #008f39;
                        border: 1px solid #4c89f7;
                    }
                    QCheckBox::indicator:unchecked {
                        background-color: #c0c0c0;
                        border: 1px solid #a0a0a0;
                    }
                """)
            else:
                checkbox.setStyleSheet("""
                                    QCheckBox {
                                        font-size: 14px;
                                        color: #333;
                                        font-family: 'Segoe UI', Arial, sans-serif;
                                        padding: 5px;
                                    }
                                    QCheckBox::indicator {
                                        width: 18px;
                                        height: 18px;
                                        border-radius: 3px;
                                    }
                                    QCheckBox::indicator:checked {
                                        background-color: #4c89f7;
                                        border: 1px solid #4c89f7;
                                    }
                                    QCheckBox::indicator:unchecked {
                                        background-color: #c0c0c0;
                                        border: 1px solid #a0a0a0;
                                    }
                                """)
            self.checkbox_layout.addWidget(checkbox, row, col, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Agregar el layout de los checkboxes al layout del contenedor
        self.checkbox_container_layout.addLayout(self.checkbox_layout)

        # Agregar el botón de "Configuración avanzada" y el contenedor al layout principal
        # Posicionar el botón de "Configuración avanzada" debajo del botón "Cargar ontología" en el layout
        self.main_layout.addWidget(self.advanced_settings_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.checkbox_container)

        self.main_layout.addWidget(self.cargar_con_excel)

        # Crear área y layout de instancias
        self.instance_area = QtWidgets.QWidget(self)
        self.instance_layout = QtWidgets.QGridLayout(self.instance_area)
        self.main_layout.addWidget(self.instance_area)

        
        # Mensaje de validación
        self.validation_label = QtWidgets.QLabel("", self)
        self.validation_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.validation_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.main_layout.addWidget(self.validation_label)

        # Mensaje de carga y ruedita
        self.loading_label = QtWidgets.QLabel("", self)
        self.loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        self.main_layout.addWidget(self.loading_label)
        # Mensaje de carga y ruedita
        self.sub_loading_label = QtWidgets.QLabel("", self)
        self.sub_loading_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.sub_loading_label.setStyleSheet("font-size: 14px; font-weight: bold; color: grey;")
        self.main_layout.addWidget(self.sub_loading_label)

        self.loading_wheel = QtWidgets.QLabel(self)
        self.loading_wheel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loading_wheel.setVisible(False)
        self.main_layout.addWidget(self.loading_wheel)

        # Cargar la animación de la ruedita giratoria
        self.movie = QtGui.QMovie("icons/mate.png")
        self.movie.setScaledSize(QtCore.QSize(40, 40))  # Ajusta a 100x100 píxeles, o el tamaño que prefieras
        self.loading_wheel.setMovie(self.movie)

        # Crear un temporizador para animar la sombra
        self.shadow_timer = QTimer()
        self.shadow_timer.timeout.connect(self.move_shadow)
        self.shadow_timer.start(30)  # Actualizar cada 30 milisegundos para un movimiento suave

        # Crear layout horizontal para el botón de ayuda
        self.manual_help_layout = QtWidgets.QHBoxLayout()

        # Crear botón con ícono
        self.manual_help_button = QtWidgets.QPushButton("📝")
        self.manual_help_button.setFixedSize(25, 25)
        self.manual_help_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                color: white;
                background-color: #4c89f7;
                border-radius: 10px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #5c9aff;
            }
        """)
        #self.manual_help_button.setIcon(QtGui.QIcon("ruta/al/icono.png"))  # Reemplaza con la ruta del ícono
        self.manual_help_button.setIconSize(QtCore.QSize(25, 25))  # Ajusta el tamaño del ícono
        self.manual_help_button.clicked.connect(self.show_manual_help_dialog)

        # Crear QLabel para el texto
        self.manual_help_label = QtWidgets.QLabel("Ver manual de usuario")
        self.manual_help_label.setStyleSheet("""
            font-size: 20px;
            color: #555555;
            font-family: 'Arial', sans-serif;
            margin-bottom: 15px;
            border: 0px solid #d3d3d3;
        """)

        # Agregar botón e ícono al layout horizontal
        self.manual_help_layout.addWidget(self.manual_help_button)
        self.manual_help_layout.addWidget(self.manual_help_label)

        # Crear un widget para contener el layout
        self.manual_help_widget = QtWidgets.QWidget()
        self.manual_help_widget.setLayout(self.manual_help_layout)

        # Agregar el widget al layout principal
        self.main_layout.addWidget(self.manual_help_widget)

    def move_shadow(self):
        # Cambia la posición de la sombra
        self.shadow_offset_x += self.shadow_direction_x
        self.shadow_offset_y += self.shadow_direction_y

        # Revertir dirección si alcanza un límite (para que vaya de un lado a otro)
        if abs(self.shadow_offset_x) > 5:
            self.shadow_direction_x *= -1
        if abs(self.shadow_offset_y) > 5:
            self.shadow_direction_y *= -1

        # Aplicar el desplazamiento de sombra
        self.shadow_effect.setXOffset(self.shadow_offset_x)
        self.shadow_effect.setYOffset(self.shadow_offset_y)
        self.first_time_label.destroyed.connect(lambda: self.shadow_timer.stop())

    def update_window_title(window, rdf_path=None):
        # Título base
        title = 'Ontology Viewer'

        # Agregar versión y path si están definidos
        title += f' - Version: v1.0.14'
        if rdf_path:
            title += f' - Archivo de ontologia: {rdf_path}'

        # Establecer el nuevo título en la ventana
        window.setWindowTitle(title)

    # Función para mostrar u ocultar el contenedor de configuración avanzada
    def toggle_advanced_settings(self):
        if self.advanced_settings_button.isChecked():
            self.checkbox_container.setVisible(True)
        else:
            self.checkbox_container.setVisible(False)



    # Función para mostrar el diálogo de ayuda con formato
    def show_help_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Información de Ayuda")
        dialog.setMinimumSize(400, 300)

        # Texto con formato HTML
        help_text = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manual de Usuario - Visualización de Ontologías</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 20px;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 5px;
        }
        h3 {
            color: #4CAF50;
            margin-top: 15px;
        }
        p, ul, li {
            margin: 10px 0;
        }
        .section {
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        img {
            display: block;
            margin: 0 auto; /* Centra las imágenes */
            max-width: 100%;
            height: auto; /* Ajusta la proporción */
        }
        .image-container {
            line-height: 0; /* Elimina espacios debajo de las imágenes */
        }
        footer {
            text-align: center;
            padding: 10px 0;
            background-color: #4CAF50;
            color: white;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Manual de Usuario: Visualización de Ontologías</h1>
        
        <div class="section">
            <h2>1. Introducción</h2>
            <p>Esta aplicación está diseñada para explorar y visualizar información contenida en ontologías RDF. No necesitas conocimientos previos sobre ontologías, ya que el sistema es intuitivo y te guía paso a paso.</p>
        </div>

        <div class="section">
            <h2>2. Pantalla Principal</h2>
            <p>Al iniciar la aplicación, encontrarás una pantalla simple con un botón grande al centro:</p>
            <ul>
                <li><strong>Botón "Cargar Ontología"</strong>: Es el punto de partida. Haz clic para cargar el archivo con el repositorio de investigaciones desde tu computadora.</li>
            </ul>
            <p>Después de cargar un archivo RDF:</p>
            <ul class="image-container">
                <li>La aplicación validará automáticamente el archivo. <br>
                <img src="manual_help_images/pantalla_principal.png" style="width: 60%;"> </li>
                <li>Si la ontología es consistente, aparecerá un mensaje en verde: <strong>"La ontología es consistente."</strong> <br>
                <img src="manual_help_images/mensaje_validacion.png" style="width: 50%;"></li>
                <li>Si no es válida, el mensaje será en rojo.</li>
            </ul>
        </div>
    </div>
</body>
</html>


        """

        # Crear un QTextEdit para mostrar el texto de ayuda
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)

        # Layout del diálogo
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        # Mostrar el diálogo
        dialog.exec()

    # Función para mostrar el diálogo de ayuda con formato
    def show_manual_help_dialog(self):
        ruta_pdf = QUrl.fromLocalFile("Manual de Usuario.pdf")
        QDesktopServices.openUrl(ruta_pdf)


    def show_info_message(self, title, message):
        # Crear un cuadro de mensaje de información
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def load_ontology(self):

        self.first_time_label.hide()
        self.first_time_label.setVisible(False)
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir archivo RDF", "", "RDF Files (*.rdf);;All Files (*)")
        if file_name:
            self.advanced_settings_button.setVisible(False)
            self.cargar_con_excel.setVisible(False)
            self.checkbox_container.setVisible(False)

            self.ontology_file = file_name
            logging.info("load_ontology - archivo " + self.ontology_file)

            if self.justLoadNoInference.isChecked():
                self.loader.validate_and_infer_ontology(file_name, False, True)

                # Cargar la ontología
                self.load_button.setVisible(False)
                self.first_time_label.hide()
                self.display_project_instances()

                # Limpiar mensajes y detener la animación de la ruedita giratoria

                self.main_layout.removeWidget(self.loading_label)
                self.loading_label.deleteLater()  # Libera el recurso del QLabel
                self.loading_label = None  # Opcional: elimina la referencia para evitar posibles errores
                self.main_layout.removeWidget(self.sub_loading_label)
                self.sub_loading_label.deleteLater()  # Libera el recurso del QLabel
                self.sub_loading_label = None  # Opcional: elimina la referencia para evitar posibles errores
                self.update_window_title(file_name)
                return

            # Validar la ontología primero
            self.validation_label.setText("Validando ontología...")
            QtCore.QCoreApplication.processEvents()  # Permitir que la interfaz procese eventos

            is_consistent = self.loader.validate_ontology(file_name)  # Validar ontología

            if is_consistent:
                self.validation_label.setText("La ontología es consistente.")
                QtCore.QCoreApplication.processEvents()
                self.main_layout.removeItem(self.spacerInit)
                del self.spacerInit  # Elimina la referencia al espaciador

            else:
                self.validation_label.setText("Error: La ontología no es consistente.")
                self.advanced_settings_button.setVisible(True)
                QtCore.QCoreApplication.processEvents()
                return  # Si no es consistente, detener el proceso

            # Forzar la actualización de la interfaz antes de continuar
            QtCore.QCoreApplication.processEvents()

            demora = 0
            # Recopilar las opciones de inferencia seleccionadas en los checkboxes
            selected_inferences = []
            if self.classAssertions_checkbox.isChecked():
                selected_inferences.append("classAssertions")
                demora += 1
            if self.propertyAssertions_checkbox.isChecked():
                selected_inferences.append("propertyAssertions")
                demora += 3
            if self.subClass_checkbox.isChecked():
                selected_inferences.append("subClass")
                demora += 1
            if self.equivalentClass_checkbox.isChecked():
                selected_inferences.append("equivalentClass")
                demora += 1
            if self.disjointClasses_checkbox.isChecked():
                selected_inferences.append("disjointClasses")
                demora += 1
            if self.equivalentObjectProperty_checkbox.isChecked():
                selected_inferences.append("equivalentObjectProperty")
                demora += 3
            if self.objectPropertyCharacteristic_checkbox.isChecked():
                selected_inferences.append("objectPropertyCharacteristic")
                demora += 3
            if self.inverseObjectProperties_checkbox.isChecked():
                selected_inferences.append("inverseObjectProperties")
                demora += 2
            if self.subObjectProperty_checkbox.isChecked():
                selected_inferences.append("subObjectProperty")
                demora += 3
            if self.dataPropertyCharacteristic_checkbox.isChecked():
                selected_inferences.append("dataPropertyCharacteristic")
                demora += 1

            if demora < 1.5:
                # Mostrar mensaje de inferencia y ruedita giratoria
                self.loading_label.setText("Realizando Inferencias")
            elif demora < 3:
                # Mostrar mensaje de inferencia y ruedita giratoria
                self.loading_label.setText("Realizando Inferencias")
                self.sub_loading_label.setText("El proceso puede tardar hasta " + str(demora) + " minutos")

            elif demora < 5:
                # Mostrar mensaje de inferencia y ruedita giratoria
                self.loading_label.setText("Realizando Inferencias")
                self.sub_loading_label.setText(
                    "El proceso puede tardar hasta " + str(demora) + " minutos. Por favor sea paciente")
            else:
                # Mostrar mensaje de inferencia y ruedita giratoria
                self.loading_label.setText("Realizando Inferencias")
                self.sub_loading_label.setText(
                    "El proceso puede tardar hasta " + str(demora) + " minutos. Por favor sea paciente")

            self.loading_wheel.setVisible(True)
            self.movie.start()

            QtCore.QCoreApplication.processEvents()  # Permitir que la interfaz procese eventos

            # Llamar a la función para validar e inferir ontología con las opciones seleccionadas

            if self.replaceFile_checkbox.isChecked():
                self.loader.validate_and_infer_ontology(file_name, False, False, selected_inferences)
                self.update_window_title(file_name)
                self.ontology_file = file_name
            else:
                self.loader.validate_and_infer_ontology(file_name, True, False, selected_inferences)
                folder_path = os.path.dirname(file_name)
                base_name = os.path.basename(file_name)
                copy_file_name = os.path.join(folder_path, f"{os.path.splitext(base_name)[0]}_INF.rdf")
                self.ontology_file = copy_file_name
                self.update_window_title(copy_file_name)

            # Cargar la ontología
            self.load_button.setVisible(False)

            self.display_project_instances()

            # Limpiar mensajes y detener la animación de la ruedita giratoria
            if is_consistent:
                self.validation_label.setText("")  # Limpiar mensaje de validación
            self.loading_label.setText("")  # Limpiar mensaje de carga

            self.main_layout.removeWidget(self.loading_label)
            self.loading_label.deleteLater()  # Libera el recurso del QLabel
            self.loading_label = None  # Opcional: elimina la referencia para evitar posibles errores
            self.main_layout.removeWidget(self.sub_loading_label)
            self.sub_loading_label.deleteLater()  # Libera el recurso del QLabel
            self.sub_loading_label = None  # Opcional: elimina la referencia para evitar posibles errores
            self.movie.stop()
            self.loading_wheel.setVisible(False)


    def run_external_program(self):
        # Ejecutar el programa `main.py` con la ruta al archivo RDF como argumento
        #subprocess.run(["venv/Scripts/python", "main.py", self.ontology_file],check=True)
        main.iniciar_app(self.ontology_file)
        if self.loader.validate_ontology(self.ontology_file):
            self.loader.load_rdf_file(self.ontology_file)  # Cargar RDF sin razonador
        else:
            self.show_info_message("Error",
                                   f"La ontologia es inconsistente, debe corregirla desde un administrador avanzado de ontologia")

    def display_project_instances(self):

        # Elimina el título (title_label) y el espaciador (spacerInit) del layout
        self.main_layout.removeWidget(self.title_label)
        #self.title_label.deleteLater()  # Libera el recurso del QLabel
        self.title_label = None  # Opcional: elimina la referencia para evitar posibles errores
        if not os.path.exists("help_init_help.txt"):
            self.first_time_label.hide()
        self.button_help_init.hide()


        # Crear un QFrame para contener el ComboBox, el botón y los textos
        project_frame = QFrame(self)
        project_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f4f8;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)

        # Crear un layout vertical para el marco que contendrá el título, subtítulo y layout del ComboBox/botón
        project_frame_layout = QVBoxLayout(project_frame)

        # Crear botones de ayuda con diferentes textos e imágenes
        button_help_explore = HelpButton("", "help_images/2_menu_exploracion_individual.png", "individual_help", self)

        project_frame_layout.addWidget(button_help_explore, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Crear el título "Explorar investigación"
        title_label = QLabel("Explorar Investigación Individual", self)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
             font-size: 26px;
            font-weight: bold;
            color: #3b5998;
            font-family: 'Arial', sans-serif;
            text-shadow: 1px 1px 3px #ccc;
            margin-bottom: 2px;
            border: none ;
        """)
        project_frame_layout.addWidget(title_label)

        # Crear el subtítulo "Seleccione una investigación para explorar..."
        subtitle_label = QLabel("Selecciona una investigación para ver toda su informacion...", self)
        subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #555555;
            font-family: 'Arial', sans-serif;
            margin-bottom: 15px;
            border: 0px solid #d3d3d3;
        """)
        project_frame_layout.addWidget(subtitle_label)

        # Crear un layout horizontal para el ComboBox y el botón "Visualizar"
        project_layout = QHBoxLayout()

        # Crear el ComboBox de instancias sin ancho fijo para que sea responsivo
        self.instance_combobox = QtWidgets.QComboBox(self)
        self.instance_combobox.setStyleSheet("""
                    QComboBox {
                        font-size: 18px;
                        padding: 5px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background-color: #f0f0f0;
                        color: #333;
                        border: 2px solid #b0b0b0;
                        border-radius: 10px;  /* Bordes redondeados */
                        padding-left: 10px;   /* Espaciado interno */
                    }
                    QComboBox:hover {
                        border-color: #7091e6;  /* Cambiar el color del borde cuando pasas el mouse */
                    }
                    QComboBox::drop-down {
                        border: none;  /* Eliminar el borde del botón desplegable */
                    }
                    QComboBox::down-arrow {
                        image: url(down_arrow_icon.png);  /* Puedes usar un icono personalizado aquí */
                        width: 14px;
                        height: 14px;
                    }
                """)
        self.instance_combobox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        # Llenar el ComboBox con las instancias de "proyecto_de_investigacion"
        project_instances = self.loader.get_project_instances()
        if not project_instances:
            print("No se encontraron instancias de 'proyecto_de_investigacion'.")

        for project_instance in project_instances:
            project_name = project_instance.split("#")[-1]
            self.instance_combobox.addItem(project_name, userData=project_instance)

        # Crear el botón "Visualizar" con tamaño fijo
        self.visualizar_button = QtWidgets.QPushButton('Explorar', self)
        self.visualizar_button.setFixedSize(100, 40)
        self.visualizar_button.clicked.connect(self.on_visualize_button_clicked)

        # Añadir el ComboBox y el botón al layout horizontal
        project_layout.addWidget(self.instance_combobox)
        project_layout.addWidget(self.visualizar_button)

        # Botón para ejecutar el programa empaquetado
        self.alta_Ontologia = QtWidgets.QPushButton("")
        self.alta_Ontologia.setStyleSheet("font-size: 18px; padding: 10px;")
        self.alta_Ontologia.setIcon(QtGui.QIcon('icons/lapiz.png'))
        self.alta_Ontologia.setToolTip("Haz clic para agregar nuevas instancias o relaciones al archivo")
        self.alta_Ontologia.clicked.connect(self.run_external_program)
        project_layout.addWidget(self.alta_Ontologia)

        # Añadir el layout horizontal al layout vertical del marco (debajo del título y subtítulo)
        project_frame_layout.addLayout(project_layout)

        # Añadir el marco completo al layout principal
        self.main_layout.addWidget(project_frame)

        # Crear la sección de "Consultas personalizadas"

        self.display_custom_queries_section()


        # Crear el área de información (info_display) pero establecerla como oculta inicialmente
        if not hasattr(self, 'info_display'):
            self.info_display = QTextEdit()
            self.info_display.setReadOnly(True)
            self.info_display.setStyleSheet("""
                background-color: #f0f0f0; font-size: 14px;
                color: black; font-family: 'Segoe UI', Arial, sans-serif;
            """)
            self.info_display.setMinimumHeight(500)
            self.info_display.setVisible(False)

        self.main_layout.addWidget(self.info_display)

    def display_project_instances_resume(self):
        # Crear un QFrame para contener el ComboBox, el botón y los textos
        project_frame = QFrame(self)
        project_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f4f8;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)

        # Crear un layout vertical para el marco que contendrá el título, subtítulo y layout del ComboBox/botón
        project_frame_layout = QVBoxLayout(project_frame)

        # Crear botones de ayuda con diferentes textos e imágenes
        button_help_explore = HelpButton("", "help_images/2_menu_exploracion_individual.png", "individual_help", self)

        project_frame_layout.addWidget(button_help_explore, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # Crear el título "Explorar investigación"
        title_label = QLabel("Explorar Investigación Individual", self)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
             font-size: 26px;
            font-weight: bold;
            color: #3b5998;
            font-family: 'Arial', sans-serif;
            text-shadow: 1px 1px 3px #ccc;
            margin-bottom: 2px;
            border: none ;
        """)
        project_frame_layout.addWidget(title_label)

        # Crear el subtítulo "Seleccione una investigación para explorar..."
        subtitle_label = QLabel("Selecciona una investigación para ver toda su informacion...", self)
        subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #555555;
            font-family: 'Arial', sans-serif;
            margin-bottom: 15px;
            border: 0px solid #d3d3d3;
        """)
        project_frame_layout.addWidget(subtitle_label)

        # Crear un layout horizontal para el ComboBox y el botón "Visualizar"
        project_layout = QHBoxLayout()

        # Crear el ComboBox de instancias sin ancho fijo para que sea responsivo
        self.instance_combobox = QtWidgets.QComboBox(self)
        self.instance_combobox.setStyleSheet("""
                    QComboBox {
                        font-size: 18px;
                        padding: 5px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        background-color: #f0f0f0;
                        color: #333;
                        border: 2px solid #b0b0b0;
                        border-radius: 10px;  /* Bordes redondeados */
                        padding-left: 10px;   /* Espaciado interno */
                    }
                    QComboBox:hover {
                        border-color: #7091e6;  /* Cambiar el color del borde cuando pasas el mouse */
                    }
                    QComboBox::drop-down {
                        border: none;  /* Eliminar el borde del botón desplegable */
                    }
                    QComboBox::down-arrow {
                        image: url(down_arrow_icon.png);  /* Puedes usar un icono personalizado aquí */
                        width: 14px;
                        height: 14px;
                    }
                """)
        self.instance_combobox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        # Llenar el ComboBox con las instancias de "proyecto_de_investigacion"
        project_instances = self.loader.get_project_instances()
        if not project_instances:
            print("No se encontraron instancias de 'proyecto_de_investigacion'.")

        for project_instance in project_instances:
            project_name = project_instance.split("#")[-1]
            self.instance_combobox.addItem(project_name, userData=project_instance)

        # Crear el botón "Visualizar" con tamaño fijo
        self.visualizar_button = QtWidgets.QPushButton('Explorar', self)
        self.visualizar_button.setFixedSize(100, 40)
        self.visualizar_button.clicked.connect(self.on_visualize_button_clicked)

        # Añadir el ComboBox y el botón al layout horizontal
        project_layout.addWidget(self.instance_combobox)
        project_layout.addWidget(self.visualizar_button)

        # Botón para ejecutar el programa empaquetado
        self.alta_Ontologia = QtWidgets.QPushButton("")
        self.alta_Ontologia.setStyleSheet("font-size: 18px; padding: 10px;")
        self.alta_Ontologia.setIcon(QtGui.QIcon('icons/lapiz.png'))
        self.alta_Ontologia.setToolTip("Haz clic para agregar nuevas instancias o relaciones al archivo")
        self.alta_Ontologia.clicked.connect(self.run_external_program)
        project_layout.addWidget(self.alta_Ontologia)

        # Añadir el layout horizontal al layout vertical del marco (debajo del título y subtítulo)
        project_frame_layout.addLayout(project_layout)

        # Añadir el marco completo al layout principal
        self.main_layout.addWidget(project_frame)

    def on_visualize_button_clicked(self):

        # Limpiar todos los elementos de la pantalla antes de cargar el nuevo contenido
        self.clear_layout(self.main_layout)
        # Crear una animación de clic en el botón
        animation = QPropertyAnimation(self.visualizar_button, b"geometry")
        animation.setDuration(150)  # Duración de la animación en milisegundos
        animation.setStartValue(self.visualizar_button.geometry())

        # Reducir ligeramente el tamaño del botón para dar un efecto de clic
        shrink_geometry = self.visualizar_button.geometry()
        shrink_geometry.setWidth(shrink_geometry.width() - 4)
        shrink_geometry.setHeight(shrink_geometry.height() - 4)
        shrink_geometry.moveCenter(self.visualizar_button.geometry().center())

        animation.setEndValue(shrink_geometry)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Iniciar la animación
        animation.start()
        # Obtener la instancia seleccionada en el ComboBox
        selected_instance = self.instance_combobox.currentData()

        if selected_instance:
            project_name = self.instance_combobox.currentText()
            self.show_project_view(selected_instance, project_name)

            # Devolver el tamaño original del botón al final de la animación
            animation.finished.connect(lambda: self.visualizar_button.setGeometry(self.visualizar_button.geometry()))

        # Buscar y eliminar solo el checkbox "infer_checkbox"
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            widget = item.widget()
            if widget is self.checkbox_layout:
                # Eliminar el checkbox encontrado
                widget.deleteLater()
                break
                # Buscar y eliminar el combobox y el botón "Visualizar"
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                widget = item.widget()

                # Verificar si el widget es el ComboBox o el botón "Visualizar"
                if isinstance(widget, QtWidgets.QComboBox) and widget is self.instance_combobox:
                    # Eliminar el ComboBox encontrado
                    widget.deleteLater()
                elif isinstance(widget, QtWidgets.QPushButton) and widget is self.visualizar_button:
                    # Eliminar el botón "Visualizar" encontrado
                    widget.deleteLater()
                # Recorrer los elementos del layout en reversa para eliminar cada uno

    def display_custom_queries_section(self):
        """
        Muestra una sección de "Consultas Personalizadas" con:
        - Un título destacado
        - Un botón especial de "Agregar consulta" debajo de la sección de pestañas
        - Pestañas para cada grupo de consultas
        - Botones de consulta organizados en pestañas de acuerdo al grupo
        - Un área de visualización de información dentro del mismo marco
        """
        # Buscar y eliminar el QGridLayout que contiene los checkboxes en el main_layout
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            widget = item.widget()

            # Si el item es un layout y es igual a checkbox_layout
            if widget is None and isinstance(item.layout(), QtWidgets.QGridLayout):
                layout = item.layout()
                if layout == self.checkbox_layout:
                    # Eliminar todos los checkboxes dentro de checkbox_layout
                    for j in reversed(range(layout.count())):
                        sub_item = layout.itemAt(j)
                        sub_widget = sub_item.widget()
                        if sub_widget:
                            sub_widget.setParent(None)  # Quitar widget del layout

                    # Eliminar el layout en sí mismo
                    self.main_layout.removeItem(item)
                    layout.deleteLater()  # Eliminar el layout
                    self.checkbox_layout = None  # Eliminar referencia

        # Crear el contenedor principal de la sección para ocupar todo el ancho
        section_container = QFrame(self)
        section_container.setStyleSheet("""
            QFrame {
                background-color: #f0f4f8;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }
        """)
        section_container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

        # Layout principal vertical de esta sección
        main_layout = QVBoxLayout(section_container)

        # Crear botones de ayuda con diferentes textos e imágenes
        button_help_global = HelpButton("", "help_images/3_menu_exploracion_global.png", "global_help", self)

        # Título destacado
        title_label = QLabel("Consultas Globales de Investigaciones", self)
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #3b5998;
            font-family: 'Arial', sans-serif;
            text-shadow: 1px 1px 3px #ccc;
            margin-bottom: 2px;
            border: none ;
        """)
        main_layout.addWidget(button_help_global,alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(title_label)


        # Subtítulo
        subtitle_label = QLabel(
            "Realiza consultas para ver información comparativa y general de todas las investigaciones...", self)
        subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 15px;
            color: #555555;
            font-family: 'Arial', sans-serif;
            margin-bottom: 5px;
            border: none ;
        """)
        main_layout.addWidget(subtitle_label)

        # Contenedor de pestañas para organizar consultas
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d3d3d3;
                background: #e0f7fa;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #4a90e2;
                color: white;
                padding: 6px 10px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                transition: background 0.3s;

            }
            QTabBar::tab:hover {
                background: #559cd1;
            }
            QTabBar::tab:selected {
                background: #357ABD;
            }
        """)

        # Diccionario para almacenar pestañas y sus layouts
        self.tabs = {}

        # Cargar las consultas desde el archivo JSON
        try:
            with open("consultas_personalizadas.json", "r") as json_file:
                data = json.load(json_file)
                queries = data.get("consultas", [])
        except Exception as e:
            logging.error(e)
            print(f"Error cargando consultas personalizadas: {e}")
            return

        # Crear pestañas por grupo
        for query in queries:
            grupo = query.get("grupo", "General")
            query_name = query.get("nombre", "Consulta")
            query_text = query.get("consulta")

            # Crear pestaña si el grupo no existe
            if grupo not in self.tabs:
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                tab_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                self.tab_widget.addTab(tab, grupo)
                self.tabs[grupo] = tab_layout

            # Añadir botón de consulta
            self.add_query_button(query_name, query_text, grupo)

        # Añadir el `QTabWidget` al layout principal
        main_layout.addWidget(self.tab_widget)

        # Crear un layout horizontal para los botones "Agregar consulta" y "Modificar JSON"
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Ajustar este valor para reducir la separación entre botones

        # Botón "Agregar consulta" debajo de las pestañas
        add_query_button = QtWidgets.QPushButton("Agregar consulta", self)
        add_query_button.setFixedSize(160, 40)
        add_query_button.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 6px;
                box-shadow: 1px 1px 2px #888888;
            }
            QPushButton:hover {
                background-color: #2b8a43;
                box-shadow: 1px 1px 5px #555555;
            }
        """)
        add_query_button.clicked.connect(self.toggle_add_query_fields)
        buttons_layout.addWidget(add_query_button)

        # Botón "Modificar JSON" debajo de las pestañas
        edit_json_button = QtWidgets.QPushButton("", self)
        edit_json_button.setFixedSize(40, 40)
        edit_json_button.setStyleSheet("""
                  QPushButton {
                      background-color: #fbbc05;
                      color: white;
                      font-size: 14px;
                      font-weight: bold;
                      border: none;
                      border-radius: 6px;
                      padding: 6px;
                      box-shadow: 1px 1px 2px #888888;
                  }
                  QPushButton:hover {
                      background-color: #e5a600;
                      box-shadow: 1px 1px 5px #555555;
                  }
              """)
        icon = QtGui.QIcon("icons/json.png")
        edit_json_button.setIcon(icon)
        edit_json_button.setToolTip("Haz clic para editar el archivo JSON")
        edit_json_button.clicked.connect(self.show_json_editor)
        buttons_layout.addWidget(edit_json_button)

        # Alinear el layout de botones a la izquierda
        buttons_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Añadir el layout de botones a la pantalla principal
        main_layout.addLayout(buttons_layout)

        # Aplicar alineación
        main_layout.setAlignment(edit_json_button, QtCore.Qt.AlignmentFlag.AlignLeft)

        # Contenedor de los campos para agregar una nueva consulta (se oculta inicialmente)
        self.fields_container = QFrame()
        self.fields_container.setVisible(False)  # Oculto inicialmente
        main_layout.addWidget(self.fields_container)

        # Crear área para mostrar la información de las consultas, con mensaje inicial
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMinimumHeight(50)  # Altura reducida inicialmente
        self.info_display.setStyleSheet("""
            background-color: #ffffff;
            font-size: 14px;
            color: #999999;
            font-family: 'Arial', sans-serif;
            border: 1px solid #d3d3d3;
            border-radius: 8px;
            padding: 10px;
        """)
        # Mensaje inicial cuando no hay nada cargado
        self.info_display.setHtml(
            "<p style='text-align: center; margin-top: 10px;'>Presione una consulta para desplegar información...</p>"
        )
        main_layout.addWidget(self.info_display)

        # Añadir contenedor de sección al layout principal de la ventana
        self.main_layout.addWidget(section_container)

    def toggle_add_query_fields(self):
        """
        Muestra u oculta los campos de texto para ingresar una nueva consulta cuando se hace clic en "Agregar consulta".
        """
        # Alternar visibilidad del contenedor de campos
        if self.fields_container.isVisible():
            self.fields_container.setVisible(False)
            return

        # Si los campos aún no se han creado, inicializarlos
        if not hasattr(self, 'group_input'):
            # Crear layout de los campos
            layout = QGridLayout(self.fields_container)
            layout.setSpacing(10)

            group_label = QLabel("Grupo:")
            self.group_input = QLineEdit(self)
            self.group_input.setPlaceholderText("Ingrese el grupo")

            name_label = QLabel("Nombre de la consulta:")
            self.name_input = QLineEdit(self)
            self.name_input.setPlaceholderText("Ingrese una breve descripcion de la consulta")

            query_label = QLabel("Texto de la consulta:")
            self.query_input = QTextEdit(self)
            self.query_input.setPlaceholderText("Ingrese el codigo de la consulta en lenguaje SPARQL. ")

            # Establecer estilo
            field_style = """
                QLineEdit, QTextEdit {
                    background-color: #f9f9f9;
                    border: 0px solid #d3d3d3;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 14px;
                    color: #333;
                }
                QLabel {
                    font-size: 14px;
                    color: #555;
                    padding: 2px;
                    border: none;
                }
            """
            self.group_input.setStyleSheet(field_style)
            self.name_input.setStyleSheet(field_style)
            self.query_input.setStyleSheet(field_style)
            group_label.setStyleSheet(field_style)
            name_label.setStyleSheet(field_style)
            query_label.setStyleSheet(field_style)

            # Añadir al layout
            layout.addWidget(group_label, 0, 0)
            layout.addWidget(self.group_input, 0, 1)
            layout.addWidget(name_label, 1, 0)
            layout.addWidget(self.name_input, 1, 1)
            layout.addWidget(query_label, 2, 0)
            layout.addWidget(self.query_input, 2, 1)

            # Botón para guardar la consulta
            self.save_button = QPushButton("Guardar consulta", self)
            self.save_button.setFixedSize(150, 35)
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #357ABD;
                }
            """)
            self.save_button.clicked.connect(self.save_new_query)
            layout.addWidget(self.save_button, 3, 1, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # Mostrar el contenedor de campos
        self.fields_container.setVisible(True)

    def save_new_query(self):
        """
        Guarda la nueva consulta en el archivo JSON y añade el nuevo botón a la pestaña del grupo correspondiente.
        """
        group = self.group_input.text()
        name = self.name_input.text()
        query_text = self.query_input.toPlainText()

        if not group or not name or not query_text:
            print("Todos los campos son necesarios")
            return

        # Cargar el archivo JSON y agregar la nueva consulta
        try:
            with open("consultas_personalizadas.json", "r") as json_file:
                data = json.load(json_file)
        except Exception as e:
            logging.error(e)
            data = {"consultas": []}

        data["consultas"].append({"grupo": group, "nombre": name, "consulta": query_text})

        with open("consultas_personalizadas.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

        # Añadir el nuevo botón a la pestaña correspondiente
        self.add_query_button(name, query_text, group)

        # Limpiar y ocultar el contenedor de campos de entrada y el botón
        self.group_input.clear()
        self.name_input.clear()
        self.query_input.clear()
        self.fields_container.hide()  # Ocultar todo el contenedor

        # Marcar los campos como no visibles
        self.fields_visible = False

    def add_query_button(self, name, query_text, group):
        """
        Crea un nuevo botón de consulta y lo añade al grupo correspondiente en la pestaña.
        """
        query_button = QPushButton(self)
        query_button.setFixedSize(40, 40)
        query_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        query_button.clicked.connect(lambda _, q=query_text: self.on_custom_query_clicked(q, ""))

        # Layout con el botón y la etiqueta de texto a la derecha
        button_layout = QHBoxLayout()
        button_layout.addWidget(query_button)

        button_label = QLabel(name, self)
        button_label.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            font-family: 'Arial', sans-serif;
            padding-left: 10px;
        """)
        button_layout.addWidget(button_label)

        button_container = QWidget()
        button_container.setLayout(button_layout)

        # Añadir el contenedor del botón al layout de la pestaña correspondiente
        if group not in self.tabs:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            self.tab_widget.addTab(tab, group)
            self.tabs[group] = tab_layout

        self.tabs[group].addWidget(button_container)

    def load_query_buttons(self):
        """
        Carga los botones de consulta desde el archivo JSON.
        """
        try:
            with open("consultas_personalizadas.json", "r") as json_file:
                data = json.load(json_file)
                queries = data.get("consultas", [])
                for query in queries:
                    self.add_query_button(query["nombre"], query["consulta"])
        except Exception as e:
            logging.error(e)
            print(f"Error cargando consultas personalizadas: {e}")

    def on_custom_query_clicked(self, query_text, project_instance):
        """
        Ejecuta la consulta SPARQL y muestra los resultados en el área de información usando display_info.
        """
        # Reemplaza el marcador {project_instance} con el valor de la variable project_instance
        query_text = query_text.replace("{project_instance}", project_instance)
        try:
            results = self.loader.graph.query(query_text)
            formatted_results = [[str(binding) for binding in result] for result in results]
            column_names = [str(var) for var in results.vars]
            self.display_info(formatted_results, column_names)

            # Mostrar info_display cuando se ejecuta una consulta
            self.info_display.setVisible(True)

        except Exception as e:
            logging.error(e)
            print(f"Error ejecutando la consulta SPARQL: {e}")

    def show_json_editor(self):
        """
        Abre una ventana de diálogo para mostrar y editar el archivo JSON de consultas personalizadas.
        """
        # Crear un cuadro de diálogo para la edición
        self.json_editor_dialog = QDialog(self)
        self.json_editor_dialog.setWindowTitle("Editor de JSON")
        self.json_editor_dialog.setMinimumSize(600, 400)

        # Crear un layout vertical para el diálogo
        dialog_layout = QVBoxLayout(self.json_editor_dialog)

        # Editor de texto para mostrar el contenido JSON
        self.json_text_edit = QTextEdit(self.json_editor_dialog)
        self.json_text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 14px;
                color: #333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                padding: 10px;
            }
        """)

        # Cargar el contenido del JSON en el editor
        try:
            with open("consultas_personalizadas.json", "r") as json_file:
                json_content = json_file.read()
                self.json_text_edit.setPlainText(json_content)
        except Exception as e:
            logging.error(e)
            print(f"Error al cargar el archivo JSON: {e}")
            self.json_text_edit.setPlainText("Error al cargar el archivo JSON.")

        dialog_layout.addWidget(self.json_text_edit)

        # Botón para guardar cambios
        save_button = QPushButton("Guardar cambios", self.json_editor_dialog)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2b8a43;
            }
        """)
        save_button.clicked.connect(self.save_json_edits)
        dialog_layout.addWidget(save_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        # Mostrar el diálogo
        self.json_editor_dialog.exec()

    def save_json_edits(self):
        """
        Guarda los cambios realizados en el archivo JSON.
        """
        # Obtener el texto modificado
        json_content = self.json_text_edit.toPlainText()

        # Intentar guardar el contenido en el archivo JSON
        try:
            # Verificar si el contenido es un JSON válido
            data = json.loads(json_content)

            # Guardar en el archivo JSON
            with open("consultas_personalizadas.json", "w") as json_file:
                json.dump(data, json_file, indent=4)

            print("Cambios guardados exitosamente.")

            # Recargar las pestañas y consultas con las modificaciones
            self.reload_custom_queries()

            # Cerrar el diálogo después de guardar
            self.json_editor_dialog.accept()

        except json.JSONDecodeError:
            logging.WARNING("El contenido no es un JSON valido." )
            print("Error: El contenido no es un JSON válido.")

    def reload_custom_queries(self):
        """
        Elimina las pestañas existentes y vuelve a cargar las consultas desde el archivo JSON.
        """
        # Limpiar las pestañas actuales
        self.tab_widget.clear()
        self.tabs = {}

        # Recargar las consultas desde el archivo JSON
        try:
            with open("consultas_personalizadas.json", "r") as json_file:
                data = json.load(json_file)
                queries = data.get("consultas", [])
        except Exception as e:
            logging.error(e)
            print(f"Error recargando consultas personalizadas: {e}")
            return

        # Crear pestañas y botones de consulta según el archivo JSON
        for query in queries:
            grupo = query.get("grupo", "General")
            query_name = query.get("nombre", "Consulta")
            query_text = query.get("consulta")

            # Crear la pestaña si el grupo no existe
            if grupo not in self.tabs:
                tab = QWidget()
                tab_layout = QVBoxLayout(tab)
                tab_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                self.tab_widget.addTab(tab, grupo)
                self.tabs[grupo] = tab_layout

            # Añadir el botón de consulta
            self.add_query_button(query_name, query_text, grupo)

    def clear_layout(self, layout):
        """
        Oculta todos los widgets en un layout dado, excepto la barra de título.
        """
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()

            # Ocultar widget o sublayout
            if widget is not None:
                widget.setVisible(False)
            elif item.layout() is not None:
                # Llama recursivamente para sublayouts
                self.clear_layout(item.layout())

    def create_instance_window(self, project_instance, project_name, row, col):
        # Crear el frame clickeable para la instancia
        instance_frame = ClickableFrame(self.instance_area)
        instance_frame.setStyleSheet("""
            background-color: #8697c4;
            border-radius: 10px;
        """)
        instance_frame.setMinimumSize(self.width() // 5, 150)

        # Asignar comportamiento del clic
        if self.is_proyecto_de_investigacion(project_instance):
            instance_frame.clicked.connect(lambda: self.show_project_view(project_instance, project_name))
        else:
            instance_frame.clicked.connect(lambda: self.on_instance_clicked(QtGui.QCursor.pos(), project_instance))

        # Crear el layout del frame
        layout = QVBoxLayout(instance_frame)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        # Etiqueta para el nombre del proyecto
        project_label = QLabel(f"INVESTIGACION: {project_name}")
        project_label.setStyleSheet("""
            font-size: 14px; font-weight: bold;
            color: black; font-family: 'Segoe UI', Arial, sans-serif;
        """)
        # Crear botones de ayuda con diferentes textos e imágenes

        layout.addWidget(project_label)

        # Agregar información adicional: Investigadores relacionados
        investigators = self.loader.get_investigators_for_project(project_instance)
        if investigators:
            investigators_names = [self.loader.get_investigator_name(inv.investigator) for inv in investigators]
            investigators_label = QLabel(f"Investigadores: {', '.join(investigators_names)}")
            investigators_label.setStyleSheet("""
                font-size: 12px; font-style: italic;
                color: black; font-family: 'Segoe UI', Arial, sans-serif;
            """)
            layout.addWidget(investigators_label)

        # Agregar el objetivo del proyecto
        objectives = self.loader.get_objectives_for_project(project_instance)
        if objectives:
            objectives_title_label = QLabel(f"Objetivos:")
            layout.addWidget(objectives_title_label)
            for objective in objectives:
                objective_description = self.loader.get_objective_description(objective.objective)
                objectives_label = QLabel(f"      {objective_description}")
                objectives_label.setStyleSheet("""
                    font-size: 12px; font-style: italic;
                    color: black; font-family: 'Segoe UI', Arial, sans-serif;
                """)
                layout.addWidget(objectives_label)

            # Agregar las estrategias metodológicas y mostrar el atributo "objetivo"
        estrategias = self.loader.get_estrategia_metodologica_for_project(project_instance)
        if estrategias:
            estrategia_title_label = QLabel(f"Estrategias Metodologicas:")
            layout.addWidget(estrategia_title_label)
            # Obtener y mostrar el valor de 'objetivo' para cada estrategia metodológica
            for estrategia in estrategias:
                estrategia_objetivo = self.loader.get_objective_objetive(estrategia[0])
                estrategia_label = QLabel(f"      {estrategia_objetivo}")
                estrategia_label.setStyleSheet("""
                       font-size: 12px; font-style: italic;
                       color: black; font-family: 'Segoe UI', Arial, sans-serif;
                   """)
                layout.addWidget(estrategia_label)

                # Obtener y mostrar las técnicas relacionadas con sus clases y núcleos
                techniques = self.loader.get_techniques_for_estrategia(estrategia[0])
                if techniques:
                    for tecnica_uri, tecnica_class, nucleo in techniques:
                        tecnica_label = QLabel(f"  {tecnica_class}, Núcleo: {nucleo}")
                        tecnica_label.setStyleSheet("""
                               font-size: 12px; font-style: italic;
                               color: black; font-family: 'Segoe UI', Arial, sans-serif;
                           """)
                        layout.addWidget(tecnica_label)
        # Agregar el objetivo del proyecto
        reportes = self.loader.get_reporte_for_project(project_instance)
        if reportes:
            conclusiones_title_label = QLabel(f"Conclusiones:")

            layout.addWidget(conclusiones_title_label)
            for reporte in reportes:
                conclusiones = self.loader.get_objective_conclusion(reporte[0])

                for conclusion in conclusiones:
                    conclusion_label = QLabel(f"      {conclusion}")
                    conclusion_label.setStyleSheet("""
                        font-size: 12px; font-style: italic;
                        color: black; font-family: 'Segoe UI', Arial, sans-serif;
                    """)
                    layout.addWidget(conclusion_label)

        # Añadir el frame al layout principal de la ventana
        self.instance_layout.addWidget(instance_frame, row, col)

    def display_buttons_between_sections(self):
        # Crear un QFrame para contener la lista de instancias inferidas y el botón de "Ver inferencias"
        inferred_frame = QFrame(self)
        inferred_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        # Crear un layout vertical para el QFrame
        inferred_layout = QVBoxLayout(inferred_frame)
        inferred_layout.setContentsMargins(20, 10, 20, 10)
        inferred_layout.setSpacing(10)

        # Título para la sección
        title_label = QLabel("Instancias Inferidas por el Razonador", self)
        # title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #4a90e2;
            font-family: 'Arial', sans-serif;
            padding: 0 10px;
            border: none;
        """)
        button_help_axiomas_individual = HelpButton("", "help_images/5_axiomas.png",
                                                   "axiomas_help", self)
        inferred_layout.addWidget(button_help_axiomas_individual,alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        inferred_layout.addWidget(title_label)

        # Botón para ver inferencias
        self.view_inferences_button = QPushButton("Ver log de inferencias realizadas", self)

        # Definir el estilo para el botón
        button_style = """
                    QPushButton {
                        font-size: 16px;
                        font-weight: bold;
                        color: #333333;
                        background-color: #f9f9f9;
                        border: 1px solid #d3d3d3;
                        border-radius: 8px;
                        padding: 10px 20px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                    QPushButton:pressed {
                        background-color: #d0d0d0;
                    }
                """
        self.view_inferences_button.setStyleSheet(button_style)
        # Crear el botón "Cargar Objetivos" y aplicar el estilo

        self.view_inferences_button.clicked.connect(self.show_inferences)
        inferred_layout.addWidget(self.view_inferences_button)

        # Contenedor de texto para mostrar el contenido del archivo de inferencias
        self.inference_text_display = QTextEdit(self)
        self.inference_text_display.setReadOnly(True)
        self.inference_text_display.setStyleSheet("""
            font-size: 14px;
            color: #333333;
            font-family: 'Arial', sans-serif;
            background-color: #ffffff;
            border: 1px solid #d3d3d3;
            padding: 10px;
            min-height: 300px;  /* Tamaño ampliado para facilitar la visualización */
        """)
        inferred_layout.addWidget(self.inference_text_display)
        self.inference_text_display.hide()  # Ocultarlo inicialmente

        # Botón para cargar más líneas
        self.load_more_button = QPushButton("Cargar más", self)
        self.load_more_button.setStyleSheet("""
            font-size: 14px;
            background-color: #4a90e2;
            color: white;
            border-radius: 5px;
            padding: 5px;
        """)
        self.load_more_button.clicked.connect(self.load_more_inferences)
        inferred_layout.addWidget(self.load_more_button)
        self.load_more_button.hide()  # Ocultarlo inicialmente

        # Añadir el frame completo al layout principal
        self.main_layout.addWidget(inferred_frame)

        # Variables para gestionar la carga de bloques
        self.current_line = 0
        self.inference_file_path = "inference_log.txt"

    def remove_duplicates(self, file_path):
        """Elimina líneas duplicadas y filtra líneas que contienen ciertos términos en el archivo especificado."""
        temp_file_path = file_path + "_temp"

        # Compilamos los términos a filtrar en una expresión regular para una verificación eficiente
        filter_terms = re.compile(
            r"pertenece a la clase 'analisis'|pertenece a la clase 'campo'|pertenece a la clase 'formulacion'|InferredDataProperty|EquivalentObjectProperties|xsd:string|FunctionalObjectProperty|CharacteristicAxiomGeneratorDisjointClasses|IrreflexiveObjectProperty|AsymmetricObjectProperty|owl:Thing|owl:topObjectProperty")

        with open(file_path, 'r') as infile, open(temp_file_path, 'w') as outfile:
            seen_lines_content = set()  # Conjunto para almacenar contenido único después de '->'

            for line in infile:
                # Comprobar si la línea contiene alguno de los términos a filtrar
                if filter_terms.search(line):
                    continue

                # Dividir la línea en dos partes usando '->' como separador y obtener el contenido después de '->'
                parts = line.split("->", 1)
                if len(parts) < 2:
                    continue  # Si la línea no tiene '->', ignorarla (evitar errores)

                content_after_arrow = parts[1].strip()  # Contenido después de '->'

                # Verificar si el contenido después de '->' ya ha sido visto
                if content_after_arrow not in seen_lines_content:
                    outfile.write(line)  # Escribir línea única en el archivo temporal
                    seen_lines_content.add(content_after_arrow)  # Marcar el contenido como visto

        os.replace(temp_file_path, file_path)

    def show_inferences(self):
        """Realiza limpieza del archivo, muestra las primeras 100 líneas, y oculta el botón 'Ver inferencias'."""
        # Primero, eliminar líneas duplicadas en el archivo de inferencias
        self.remove_duplicates(self.inference_file_path)

        self.inference_text_display.clear()  # Limpiar el área de texto
        self.current_line = 0  # Reiniciar el contador de líneas
        self.view_inferences_button.hide()  # Ocultar el botón "Ver inferencias"

        # Abrir el archivo una vez y guardar la referencia para cargar en bloques
        try:
            self.inference_file = open(self.inference_file_path, 'r')  # Mantener archivo abierto
        except Exception as e:
            logging.error(e)
            self.inference_text_display.setText("<p style='color: red;'>Archivo de inferencias no encontrado.</p>")
            return

        self.load_more_inferences()  # Cargar las primeras líneas
        self.inference_text_display.show()  # Mostrar el área de texto
        self.load_more_button.show()  # Mostrar el botón de cargar más

    def load_more_inferences(self):
        """Carga 100 líneas adicionales del archivo de inferencias, formateadas con HTML y sin prefijo."""
        lines_to_display = []
        prefix = "<http://www.semanticweb.org/tesis_inv_cualitativa#"
        try:
            with open(self.inference_file_path, 'r') as file:
                # Saltar líneas ya cargadas
                for _ in range(self.current_line):
                    file.readline()

                # Leer el siguiente bloque de 100 líneas
                for _ in range(100):
                    line = file.readline()
                    if not line:
                        break
                    # Eliminar el prefijo y agregar HTML para formatear el texto
                    cleaned_line = line.replace(prefix, "").replace(">", "")

                    # Dividir el nombre de la instancia del resto del texto
                    instance_name, *rest_of_line = cleaned_line.split(" ", 1)
                    rest_of_line = " ".join(rest_of_line)

                    # Determinar el icono según el tipo de inferencia
                    if "pertenece a la clase" in cleaned_line:
                        icon = "&#x1F4CC;"  # 📌 Pin para inferencias de clase
                    elif "tiene la relación" in cleaned_line:
                        icon = "&#x1F50D;"  # 🔍 Lupa para inferencias de relación
                    else:
                        icon = "&#x1F4A1;"  # 💡 (Idea) icono genérico si no coincide ninguna

                    # Formatear la línea con el nuevo estilo
                    formatted_line = (
                        f"<div style='display: flex; align-items: center; padding: 10px; "
                        f"margin: 8px 0; background-color: #e0f2ff; color: #000000; border-radius: 8px; "
                        f"border: 3px solid #007acc; font-family: Arial, sans-serif; font-size: 16px;'>"
                        f"<span style='font-size: 20px; color: #007acc;'>{icon}</span>"  # Icono dinámico
                        f"<span style='margin-left: 10px; color: #007acc; font-weight: bold;'>{instance_name}</span>"  # Nombre en azul más oscuro
                        f"<span style='margin-left: 8px;'>{rest_of_line}</span>"  # Resto de la línea en negro
                        f"</div>"
                    )
                    lines_to_display.append(formatted_line)

                # Actualizar la posición actual en el archivo
                self.current_line += len(lines_to_display)

                # Agregar las líneas al display con HTML
                self.inference_text_display.append("".join(lines_to_display))

                # Si no hay más líneas, ocultar el botón de cargar más
                if len(lines_to_display) < 100:
                    self.load_more_button.hide()

        except Exception as e:
            logging.warning(e)
            self.inference_text_display.setHtml("<p style='color: red;'>El archivo de inferencias no se encontró.</p>")

    def update_button_style(self, button, is_active):
        """
        Actualiza el estilo del botón según si la sección está activa o no.
        """
        button.setProperty("active", str(is_active).lower())
        button.style().unpolish(button)
        button.style().polish(button)

    def show_project_view(self, project_instance, project_name):
        # Buscar y eliminar solo el checkbox "infer_checkbox"
        # for i in range(self.main_layout.count()):
        #     item = self.main_layout.itemAt(i)
        #     widget = item.widget()
        #     if isinstance(widget, QtWidgets.QCheckBox) and widget is self.infer_checkbox:
        #         # Eliminar el checkbox encontrado
        #         widget.deleteLater()
        #         break

        # Crear un QFrame para contener el título y la sección de investigadores
        project_frame = QFrame(self)
        project_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        # Crear un layout vertical para el marco que contenga el título y los investigadores
        project_layout = QVBoxLayout(project_frame)
        project_layout.setContentsMargins(10, 10, 10, 10)
        project_layout.setSpacing(15)

        # Crear el título del proyecto
        self.display_project_instances_resume()
        project_title = QLabel(f"INVESTIGACION: {project_name}")
        project_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        project_title.setStyleSheet("""
                   font-size: 25px;
                   font-weight: bold;
                   color: #4a90e2;
                   font-family: 'Arial', sans-serif;
                   margin-bottom: 2px;
                   border: none ;
               """)
        project_layout.addWidget(project_title)

        # Mostrar la sección de Investigadores dentro del marco
        investigators_layout = QVBoxLayout()  # Crear un layout para los investigadores
        self.display_investigators(project_instance, layout=investigators_layout)
        project_layout.addLayout(investigators_layout)

        # Crear y agregar el botón en la esquina inferior derecha
        diagram_button = QtWidgets.QPushButton("")
        diagram_button.setFixedSize(40, 40)  # Tamaño pequeño del botón
        diagram_button.setStyleSheet("""
             QPushButton {
                 font-size: 12px;
                 background-color: #0078d7;
                 color: white;
                 border-radius: 5px;
             }
             QPushButton:hover {
                 background-color: #005fa3;
             }
         """)
        icon = QtGui.QIcon("icons/ojo.png")
        diagram_button.setIcon(icon)

        # Agregar un tooltip (mensaje de ayuda) al botón
        diagram_button.setToolTip("Haz clic para ver el diagrama")

        # Crear un layout horizontal para mantener el botón en la esquina inferior derecha
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()  # Espacio flexible para empujar el botón a la derecha
        button_help_titulo_individual = HelpButton("", "help_images/4_titulo_consulta_individual.png","individual_titulo_help", self)
        project_layout.addWidget(button_help_titulo_individual,alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        button_layout.addWidget(diagram_button)
        project_layout.addLayout(button_layout)

        # Conectar el botón a la función que muestra la imagen
        diagram_button.clicked.connect(self.show_diagram_image)

        # Añadir el marco completo al layout principal
        self.main_layout.addWidget(project_frame)

        # Continuar mostrando las otras secciones en el layout principal fuera del marco
        self.display_new_section(project_instance)
        self.display_buttons_between_sections()

        button_help_explora_clases = HelpButton("", "help_images/6_explorador_clases.png",
                                                "explora_clases_help", self)
        self.main_layout.addWidget(button_help_explora_clases, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        self.tab_widgetPrincipal = QtWidgets.QTabWidget()  # Crea el widget de pestañas
        self.main_layout.addWidget(self.tab_widgetPrincipal)  # Añade el QTabWidget al layout principal
        self.setLayout(self.main_layout)  # Configura el layout en la ventana principal



        self.display_objectives(project_instance)
        self.display_marco_teorico(project_instance)
        self.display_bibliografia(project_instance)
        self.display_estrategia_metodologica(project_instance)
        self.display_tecnica(project_instance)
        self.display_sujeto_u_objeto(project_instance)
        self.display_soporte(project_instance)
        self.display_registro(project_instance)
        self.display_informacion(project_instance)
        self.display_metadatos(project_instance)
        self.display_esquema_clasificacion_descriptiva(project_instance)
        self.display_esquema_clasificacion_analitica(project_instance)
        self.display_reporte(project_instance)

    def show_diagram_image(self):
        # Crear una ventana flotante para mostrar la imagen y guardarla en self para persistencia
        self.diagram_window = QtWidgets.QWidget()
        self.diagram_window.setWindowTitle("Diagrama")
        self.diagram_window.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.diagram_window.resize(600, 600)  # Tamaño inicial de la ventana (ajustable)

        # Crear un QLabel para mostrar la imagen
        image_label = QtWidgets.QLabel(self.diagram_window)
        pixmap = QtGui.QPixmap("icons/diagrama.png")
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)  # Escala la imagen para ajustar el QLabel
        image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Layout para centrar la imagen en la ventana flotante
        layout = QtWidgets.QVBoxLayout(self.diagram_window)
        layout.addWidget(image_label)
        self.diagram_window.setLayout(layout)

        # Mostrar la ventana flotante
        self.diagram_window.show()

    def display_new_section(self, project_instance):

        # Crear el QFrame para la nueva sección "Resumen"
        section_frame = QFrame(self)
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        # Layout para la sección
        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(10, 10, 10, 10)
        section_layout.setSpacing(15)

        # Agregar el título de la sección 'Resumen'
        section_title = QLabel("Consultas predefinidas")
        section_title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #4a90e2;
            font-family: 'Arial', sans-serif;
            margin-bottom: 2px;
            border: none ;
        """)
        section_layout.addWidget(section_title)

        # Subtítulo
        subtitle_label = QLabel("Seleccione o ingrese una consulta para realizar sobre la investigacion elegida...",
                                self)
        # subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
                    font-size: 15px;
                    color: #555555;
                    font-family: 'Arial', sans-serif;
                    margin-bottom: 5px;
                    border: none ;
                """)
        section_layout.addWidget(subtitle_label)

        # Crear un QTabWidget para las pestañas
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d3d3d3;
                background: #e0f7fa;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #4a90e2;
                color: white;
                padding: 6px 10px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                transition: background 0.3s;
            }
            QTabBar::tab:hover {
                background: #559cd1;
            }
            QTabBar::tab:selected {
                background: #357ABD;
            }
        """)

        tabs = {}

        # Cargar datos desde el archivo JSON
        try:
            with open("preguntas_competencia.json", "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
                queries = data.get("consultas", [])
        except Exception as e:
            logging.error(e)
            print(f"Error cargando consultas dinámicas: {e}")
            return

        # Crear pestañas y botones según los datos del JSON
        for query in queries:
            grupo = query.get("grupo", "General")
            nombre = query.get("nombre", "Consulta")
            consulta = query.get("consulta", "")

            if grupo not in tabs:
                tab = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
                tab_widget.addTab(tab, grupo)
                tab.setLayout(tab_layout)
                tabs[grupo] = tab_layout

            row_layout = QHBoxLayout()
            button = QPushButton()
            button.setFixedSize(40, 40)
            button.setStyleSheet("""
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            """)
            button.clicked.connect(
                lambda _, query_text=consulta: self.on_custom_query_clicked(query_text, project_instance))
            row_layout.addWidget(button)

            label_text = QLabel(nombre)
            label_text.setStyleSheet("""
                font-size: 14px;
                color: #333333;
                font-family: 'Arial', sans-serif;
                padding-left: 10px;
            """)
            row_layout.addWidget(label_text)
            row_layout.addStretch()

            tabs[grupo].addLayout(row_layout)

        section_layout.addWidget(tab_widget)

        # Crear área para mostrar la información de las consultas, inicialmente con el mensaje informativo
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMinimumHeight(50)  # Altura reducida inicialmente
        self.info_display.setStyleSheet("""
            background-color: #ffffff;
            font-size: 14px;
            color: #999999;
            font-family: 'Arial', sans-serif;
            border: 1px solid #d3d3d3;
            border-radius: 8px;
            padding: 10px;
            min-height: 50px;
        """)
        # Mensaje inicial
        self.info_display.setHtml(
            "<p style='text-align: center; margin-top: 10px;'>Presione una consulta para desplegar información...</p>")
        section_layout.addWidget(self.info_display)

        self.main_layout.addWidget(section_frame)

    def on_button_clicked(self, button, data, column_names):
        if self.selected_button:
            self.selected_button.setStyleSheet("""
                background-color: #7091e6;
                color: white;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
        button.setStyleSheet("""
            background-color: #7091e6;
            color: white;
            font-size: 16px;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 3px solid #FFD700;
        """)
        self.selected_button = button

        self.display_info(data, column_names)

    def display_info(self, data, column_names):
        if not hasattr(self, 'info_display'):
            self.info_display = QTextEdit()
            self.info_display.setReadOnly(True)
            self.info_display.setStyleSheet("""
                background-color: #f0f0f0;
                font-size: 14px;
                color: black;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            self.info_display.setMinimumHeight(50)
            self.main_layout.addWidget(self.info_display)

        # Si hay datos, expandimos el cuadro y mostramos la información
        if data:
            self.info_display.clear()
            self.info_display.setMinimumHeight(400)  # Expande el cuadro
            self.info_display.setStyleSheet("""
                background-color: #ffffff;
                font-size: 14px;
                color: #333333;
                font-family: 'Arial', sans-serif;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px;
            """)

            # Función recursiva para agrupar las filas de acuerdo con las columnas
            def group_by_columns(data, column_index=0):
                if column_index >= len(column_names):
                    return data  # No hay más columnas para agrupar, devolver los datos

                grouped_data = {}
                for row in data:
                    column_value = str(row[column_index]).split("#")[-1]

                    if column_value not in grouped_data:
                        grouped_data[column_value] = []
                    grouped_data[column_value].append(row)

                for key in grouped_data:
                    grouped_data[key] = group_by_columns(grouped_data[key], column_index + 1)

                return grouped_data

            grouped_data = group_by_columns(data)

            # Formatear el HTML para mostrar los datos agrupados
            def format_grouped_data(grouped_data, column_names, indent=""):
                formatted_text = """
                <style>
                    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
                    td, th { border: 2px solid #ddd; padding: 8px; vertical-align: top; width: 100%; }
                    th { background-color: #d9edf7; font-weight: bold; font-size: 16px; }
                    .level1 { background-color: #b3e5fc; font-size: 16px; font-weight: bold; padding-left: 10px; width: 100%; }
                    .level2 { background-color: #e1f5fe; font-size: 14px; font-weight: bold; padding-left: 30px; color: #333; width: 100%; }
                    .level3 { background-color: #f0f4c3; font-size: 13px; font-weight: bold; padding-left: 50px; color: #555; width: 100%; }
                    .attribute-name { font-weight: bold; text-decoration: underline; }
                    .attribute-value { color: #333; }
                    .classes { font-style: italic; color: #666; margin-top: 5px; }
                </style>
                <table>
                """

                base_uri = "http://www.semanticweb.org/tesis_inv_cualitativa#"

                for level1_key, level1_group in grouped_data.items():
                    level1_uri = level1_key if level1_key.startswith(base_uri) else f"{base_uri}{level1_key}"
                    level1_classes = ", ".join(self.loader.get_classes_for_instance(level1_uri))
                    level1_attributes = self.loader.get_attributes_for_instance(level1_uri)
                    level1_attribute_text = "<br>".join([
                        f"<span class='attribute-name'>{attr.split(':')[0]}:</span> <span class='attribute-value'>{attr.split(':', 1)[1]}</span>"
                        for attr in level1_attributes
                    ])

                    # Fila de Nivel 1 con nombre, clases y atributos
                    formatted_text += f"""
                    <tr>
                        <td colspan="2" class="level1">{column_names[0]}: {level1_key}<br>
                        <span class="classes">Clases: {level1_classes}</span><br>
                        {level1_attribute_text}</td>
                    </tr>
                    """

                    if isinstance(level1_group, dict):
                        for level2_key, level2_group in level1_group.items():
                            level2_uri = level2_key if level2_key.startswith(base_uri) else f"{base_uri}{level2_key}"
                            level2_classes = ", ".join(self.loader.get_classes_for_instance(level2_uri))
                            level2_attributes = self.loader.get_attributes_for_instance(level2_uri)
                            level2_attribute_text = "<br>".join([
                                f"<span class='attribute-name'>{attr.split(':')[0]}:</span> <span class='attribute-value'>{attr.split(':', 1)[1]}</span>"
                                for attr in level2_attributes
                            ])

                            # Fila de Nivel 2 con nombre, clases y atributos
                            formatted_text += f"""
                            <tr>
                                <td colspan="2" class="level2">{column_names[1]}: {level2_key}<br>
                                <span class="classes">Clases: {level2_classes}</span><br>
                                {level2_attribute_text}</td>
                            </tr>
                            """

                            if isinstance(level2_group, dict):
                                for level3_key, level3_group in level2_group.items():
                                    level3_uri = level3_key if level3_key.startswith(
                                        base_uri) else f"{base_uri}{level3_key}"
                                    level3_classes = ", ".join(self.loader.get_classes_for_instance(level3_uri))
                                    level3_attributes = self.loader.get_attributes_for_instance(level3_uri)
                                    level3_attribute_text = "<br>".join([
                                        f"<span class='attribute-name'>{attr.split(':')[0]}:</span> <span class='attribute-value'>{attr.split(':', 1)[1]}</span>"
                                        for attr in level3_attributes
                                    ])

                                    # Fila de Nivel 3 con nombre, clases y atributos
                                    level3_title = column_names[2] if len(column_names) > 2 else "Instancia"
                                    formatted_text += f"""
                                    <tr>
                                        <td colspan="2" class="level3">{level3_title}: {level3_key}<br>
                                        <span class="classes">Clases: {level3_classes}</span><br>
                                        {level3_attribute_text}</td>
                                    </tr>
                                    """

                formatted_text += "</table>"
                return formatted_text

            # Formatear y mostrar datos
            formatted_text = format_grouped_data(grouped_data, column_names)
            self.info_display.setHtml(formatted_text)
        else:
            # Si no hay datos, muestra el mensaje de guía y reduce el tamaño
            self.info_display.setMinimumHeight(50)
            self.info_display.setHtml(
                "<p style='text-align: center; margin-top: 10px;'>Presione una consulta para desplegar información...</p>")

    def on_instance_clicked(self, mouse_pos, instance_uri):
        self.show_properties_dialog(mouse_pos, instance_uri)

    def show_properties_dialog(self, mouse_pos, instance_uri):
        """
        Muestra las propiedades de una instancia en una ventana flotante.
        """
        properties_dialog = QDialog(self)
        properties_dialog.setWindowTitle(f"Propiedades de {instance_uri.split('#')[-1]}")
        properties_dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
            }
            QLabel {
                color: #d3d3d3;
                font-size: 16px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
        """)

        # Create properties text widget
        properties_text = QTextEdit(properties_dialog)
        properties_text.setReadOnly(True)

        # Set properties info with a styled header
        properties_info = self.loader.get_properties_for_instance(instance_uri)
        formatted_text = f"<b>{instance_uri.split('#')[-1]}</b><br><br>{properties_info}"
        properties_text.setHtml(formatted_text)

        # Position and layout settings
        properties_dialog.move(mouse_pos)
        layout = QVBoxLayout(properties_dialog)
        layout.addWidget(properties_text)
        layout.setContentsMargins(10, 10, 10, 10)
        properties_dialog.setMinimumSize(350, 250)
        properties_dialog.exec()

    def is_proyecto_de_investigacion(self, instance_uri):
        """
        Verifica si una instancia es de tipo 'proyecto_de_investigacion'.
        """
        query = f"""
        ASK WHERE {{
            <{instance_uri}> rdf:type <http://www.semanticweb.org/tesis_inv_cualitativa#proyecto_de_investigacion> .
        }}
        """
        try:
            result = self.loader.graph.query(query)
            return bool(result.askAnswer)
        except Exception as e:
            logging.error(e)
            print(f"Error al ejecutar la consulta SPARQL: {e}")
            return False

    def display_section(self, title, instances, get_func1, get_func2, get_func3, get_func4, column_titles,
                        show_list=False, layout=None):
        if layout is None:
            layout = QVBoxLayout()

        # Estilo de título de la sección, en armonía con info_display
        header_layout = QHBoxLayout()
        section_title = QLabel(title)
        section_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #244855;
            padding: 5px;
            background-color: #d9edf7;
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(section_title)

        # Botones de vista (lista, tabla, texto) con estilo más armonioso
        button_style = """
            background-color: #244855; 
            color: #f0f0f0; 
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        """
        btn_view_list = QtWidgets.QPushButton("")
        btn_view_list.setFixedSize(50, 50)
        btn_view_list.setStyleSheet(button_style)
        btn_view_list.setIcon(QtGui.QIcon('icons/img_3.png'))
        btn_view_list.setIconSize(QtCore.QSize(40, 40))
        header_layout.addWidget(btn_view_list)

        btn_view_table = QtWidgets.QPushButton("")
        btn_view_table.setFixedSize(50, 50)
        btn_view_table.setStyleSheet(button_style)
        btn_view_table.setIcon(QtGui.QIcon('icons/img_2.png'))
        btn_view_table.setIconSize(QtCore.QSize(40, 40))
        header_layout.addWidget(btn_view_table)

        btn_view_text = QtWidgets.QPushButton("")
        btn_view_text.setFixedSize(50, 50)
        btn_view_text.setStyleSheet(button_style)
        btn_view_text.setIcon(QtGui.QIcon('icons/img.png'))
        btn_view_text.setIconSize(QtCore.QSize(40, 40))
        header_layout.addWidget(btn_view_text)

        layout.addLayout(header_layout)

        # List widget, styled to be consistent with info_display
        list_widget = QWidget()
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        max_columns = 5
        col, row = 0, 0

        for instance in instances:
            instance_name = instance[0].split("#")[-1]
            instance_button = QtWidgets.QPushButton(instance_name)
            instance_button.setStyleSheet("""
                background-color: #b3e5fc; 
                color: #244855;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #244855;
                border-radius: 5px;
                padding: 5px;
            """)
            instance_button.setFixedSize(200, 50)
            instance_button.clicked.connect(
                lambda checked, uri=instance[0]: self.show_properties_dialog(QtGui.QCursor.pos(), uri))
            grid_layout.addWidget(instance_button, row, col)
            col += 1
            if col == max_columns:
                col = 0
                row += 1

        list_widget.setLayout(grid_layout)
        layout.addWidget(list_widget)

        # Table widget with harmonized style
        table_widget = self.create_table_widget(instances, get_func1, get_func2, get_func3, get_func4, column_titles)
        table_widget.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 14px;
            color: black;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 1px solid #ddd;
        """)
        layout.addWidget(table_widget)

        # Text widget with a harmonized style
        text_widget = QTextEdit()
        text_widget.setStyleSheet("""
            background-color: #ede8f5;
            color: #244855;
            font-size: 16px;
            padding: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
            border: 1px solid #ddd;
        """)
        text_widget.setReadOnly(True)
        text_content = self.create_plain_text(instances, get_func1, get_func2, get_func3, get_func4)
        text_widget.setHtml(text_content)
        text_widget.setFixedHeight(400)
        layout.addWidget(text_widget)

        # Layout for the download button, styled to blend in
        download_layout = QHBoxLayout()
        download_layout.addStretch()  # Spacer to align button to the right
        btn_download_table = QtWidgets.QPushButton("")
        btn_download_table.setFixedSize(20, 20)
        btn_download_table.setIcon(QtGui.QIcon('icons/desc.png'))
        btn_download_table.setIconSize(QtCore.QSize(20, 20))
        btn_download_table.setStyleSheet("""
            background-color: #d9edf7;
            border-radius: 5px;
            border: none;
        """)
        download_layout.addWidget(btn_download_table)
        btn_download_table.setToolTip("Haz clic para descargar como csv")
        layout.addLayout(download_layout)

        # Connect the download button
        btn_download_table.clicked.connect(lambda: self.download_table_as_csv(table_widget, title))

        # Toggle between list, table, and text view
        btn_view_list.clicked.connect(lambda: self.toggle_view(list_widget, table_widget, text_widget, "list"))
        btn_view_table.clicked.connect(lambda: self.toggle_view(list_widget, table_widget, text_widget, "table"))
        btn_view_text.clicked.connect(lambda: self.toggle_view(list_widget, table_widget, text_widget, "text"))

        # Show list or text by default based on show_list parameter
        self.toggle_view(list_widget, table_widget, text_widget, "list" if show_list else "text")

    def download_table_as_csv(self, table_widget, title):
        # Configurar opciones para el diálogo de guardar archivo
        options = QFileDialog.Option.DontUseNativeDialog

        # Abrir diálogo para guardar el archivo
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar tabla como CSV",
            f"{title}.csv",
            "CSV Files (*.csv);;All Files (*)",
            options=options
        )

        # Verificar si se ha seleccionado un archivo
        if not file_path:
            return  # Si no se selecciona archivo, salir

        # Expresión regular para eliminar etiquetas HTML
        clean_html = re.compile('<.*?>')

        # Crear archivo CSV y escribir contenido de la tabla
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Obtener los encabezados de las columnas
            headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
            writer.writerow(headers)

            # Obtener las filas de la tabla, limpiando etiquetas HTML si es necesario
            for row in range(table_widget.rowCount()):
                row_data = []

                for col in range(table_widget.columnCount()):
                    if table_widget.cellWidget(row, col):  # Si la celda es un widget (como QLabel)
                        label = table_widget.cellWidget(row, col).layout().itemAt(0).widget()
                        cell_text = label.text() if label else ''
                    else:  # Si la celda es un QTableWidgetItem
                        cell_item = table_widget.item(row, col)
                        cell_text = cell_item.text() if cell_item else ''

                    # Limpiar etiquetas HTML en el texto si es necesario
                    cell_text = re.sub(clean_html, '', cell_text)
                    row_data.append(cell_text)

                writer.writerow(row_data)

        print("Tabla guardada exitosamente en:", file_path)

    def toggle_view(self, list_widget, table_widget, text_widget, mode):
        """
        Alterna entre la vista de lista, tabla y texto.

        list_widget: Widget que contiene la lista de botones.
        table_widget: Widget que contiene la tabla.
        text_widget: Widget que contiene el texto plano.
        mode: Modo a mostrar ("list", "table", "text").
        """
        list_widget.setVisible(mode == "list")
        table_widget.setVisible(mode == "table")
        text_widget.setVisible(mode == "text")

    def create_table_widget(self, instances, get_func1, get_func2, get_func3, get_func4, column_titles):
        """
        Crea un widget con una tabla que muestra las instancias.

        instances: Lista de instancias.
        get_func1 - get_func4: Funciones para obtener el valor de cada instancia.
        column_titles: Lista con los títulos de las columnas para la tabla.
        """
        column_count = len(column_titles)
        table = QTableWidget()
        table.setColumnCount(column_count)
        table.setHorizontalHeaderLabels(column_titles)
        table.setFixedHeight(200)
        table.setRowCount(len(instances))

        # Ajustar el tamaño de las columnas para mostrar el contenido adecuadamente
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # Ajusta automáticamente el ancho de las columnas
        table.horizontalHeader().setStretchLastSection(True)

        # Configuración de estilo para el encabezado de la tabla
        table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #4a90e2;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 4px;
                border: 1px solid #d3d3d3;
            }
        """)

        clean_html = re.compile('<.*?>')  # Expresión regular para eliminar etiquetas HTML

        for row, instance in enumerate(instances):
            # Columna de nombre de instancia (sin HTML)
            inst_name = instance[0].split("#")[-1]
            inst_name_item = QTableWidgetItem(inst_name)
            inst_name_item.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Weight.Bold))  # Estilo de texto en negrita
            table.setItem(row, 0, inst_name_item)

            # Columnas de datos con posible contenido HTML
            for col, get_func in enumerate([get_func1, get_func2, get_func3, get_func4], start=1):
                inst_value = get_func(instance[0])

                # Si el valor es una lista, unir en una sola cadena separada por comas
                if isinstance(inst_value, list):
                    inst_value = ", ".join(inst_value)

                # Verificar si el valor contiene HTML
                if '<' in inst_value and '>' in inst_value:
                    # Usar QLabel para interpretar HTML
                    label = QLabel(inst_value)
                    label.setTextFormat(QtCore.Qt.TextFormat.RichText)  # Permitir formato HTML
                    label.setWordWrap(True)  # Permitir que el texto se ajuste dentro de la celda

                    # Crear un contenedor para el QLabel y agregarlo a la tabla
                    container = QWidget()
                    layout = QVBoxLayout()
                    layout.addWidget(label)
                    layout.setContentsMargins(0, 0, 0, 0)
                    container.setLayout(layout)
                    table.setCellWidget(row, col, container)
                else:
                    # Si no es HTML, simplemente usar QTableWidgetItem
                    item = QTableWidgetItem(re.sub(clean_html, '', inst_value))
                    item.setFont(QtGui.QFont("Arial", 11))  # Ajuste de estilo en el texto
                    table.setItem(row, col, item)

        # Configuración de estilo general de la tabla
        table.setStyleSheet("""
            QTableWidget {
                background-color: #f4f3fa;
                color: #333333;
                border: 1px solid #d3d3d3;
                gridline-color: #d3d3d3;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #c0c0ff;  # Color de fondo para selección
                color: white;
            }
        """)

        return table

    def create_plain_text(self, instances, get_func1, get_func2, get_func3, get_func4):
        """
        Crea el contenido de texto plano con todos los atributos, relaciones y objetivos relacionados de las instancias
        usando `get_properties_for_instance` y `get_objective_related`.
        Cada instancia se separa con una línea negra.
        """
        plain_text = ""
        for instance in instances:
            inst_name = instance[0].split("#")[-1]

            # Obtener todas las propiedades de la instancia usando `get_properties_for_instance`
            inst_data = self.loader.get_attributes_for_instance(instance[0])

            # Verificar si `inst_data` es una lista y, si es así, convertirla en una cadena
            if isinstance(inst_data, list):
                inst_data = "\n".join(inst_data)  # Convertir lista en una cadena separada por saltos de línea

            # Reemplazar saltos de línea por etiquetas <br> en `inst_data`
            inst_data_formatted = inst_data.replace("\n", "<br>")

            # Obtener objetivos relacionados usando `get_objective_related`
            objective_data = self.loader.get_objective_related(instance[0])

            # Verificar si `objective_data` es una lista y convertir a cadena si es necesario
            if isinstance(objective_data, list):
                objective_data = "\n".join(objective_data)

            # Reemplazar saltos de línea en `objective_data`
            objective_data_formatted = objective_data.replace("\n", "<br>")

            # Construir el contenido en HTML
            plain_text += f"★ <b>{inst_name}</b><br><br>{inst_data_formatted}<br><br><b>Objetivos Relacionados:</b><br>{objective_data_formatted}<hr>"

        return plain_text

    def display_investigators(self, project_instance, layout=None):
        """
        Muestra la información de los investigadores asociados al proyecto.
        Si se proporciona un layout, agrega los widgets a ese layout;
        de lo contrario, los agrega a self.main_layout.
        """
        # Usar el layout proporcionado, o por defecto usar self.main_layout
        target_layout = layout if layout is not None else self.main_layout

        # Obtener los investigadores asociados al proyecto
        investigators = self.loader.get_investigators_for_project(project_instance)

        if investigators:
            # Crear un layout horizontal para los participantes
            participants_layout = QHBoxLayout()
            participants_layout.setContentsMargins(20, 5, 0, 0)

            # Etiqueta "Participantes:" en negrita
            participants_label = QLabel("Participantes: ")
            participants_label.setStyleSheet("""
                font-size: 18px; font-weight: bold;
                color: black; font-family: 'Segoe UI', Arial, sans-serif;
                 border: 0px solid #d3d3d3;
            """)
            participants_layout.addWidget(participants_label)

            # Añadir cada investigador al layout de participantes
            for index, inv in enumerate(investigators):
                # Obtener el nombre del investigador
                inv_name = self.loader.get_investigator_name(inv.investigator)

                # Crear un ClickableFrame para cada investigador
                inv_label = ClickableFrame(self.instance_area)
                inv_label.setStyleSheet("""
                    font-size: 16px; font-style: italic;
                    color: black; font-family: 'Segoe UI', Arial, sans-serif;
                    border: 0px solid #d3d3d3;
                    border-radius: 8px;
                    padding: 10px;
                """)
                # Quitar el tamaño mínimo para permitir que se ajuste al contenido
                inv_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

                # Conectar el clic en el investigador con la función de mostrar propiedades
                inv_label.clicked.connect(
                    lambda inv=inv.investigator: self.show_properties_dialog(QtGui.QCursor.pos(), inv))

                # Layout vertical dentro del ClickableFrame para mostrar el nombre
                inv_inner_layout = QVBoxLayout(inv_label)
                inv_inner_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes internos
                name_label = QLabel(f"{inv_name}")
                name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                inv_inner_layout.addWidget(name_label)

                # Agregar el investigador al layout de participantes
                participants_layout.addWidget(inv_label)

                # Agregar un separador "|" entre los investigadores
                if index < len(investigators) - 1:
                    separator_label = QLabel("  |  ")
                    separator_label.setStyleSheet("""
                        font-size: 16px; color: black;
                        font-family: 'Segoe UI', Arial, sans-serif;
                         border: 0px solid #d3d3d3;
                    """)
                    participants_layout.addWidget(separator_label)

            # Añadir el layout de participantes al layout destino
            target_layout.addLayout(participants_layout)

    def add_expandable_panel(self, title, content_widget):
        # Crear el botón de encabezado para el panel
        header_button = QtWidgets.QPushButton(title)
        header_button.setCheckable(True)  # Permitir alternar expandido/colapsado
        header_button.setMaximumWidth(300)  # Limitar el ancho del botón

        # Estilos para mejorar la apariencia del botón
        header_button.setStyleSheet("""
            QPushButton {
        font-weight: bold;
        font-size: 14px;
        text-align: left;
        padding: 10px;
        background-color: #444444;
        color: white;
        border-radius: 10px;
        margin-bottom: 5px;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QPushButton:checked {
        background-color: #666666;
    }
        """)

        # Crear un ícono de flecha que indique el estado expandido o colapsado
        header_button.setIcon(QtGui.QIcon("icons/arrow_down.png"))  # Usa un ícono de flecha abajo
        header_button.setIconSize(QtCore.QSize(16, 16))  # Tamaño del ícono

        # Cambiar el ícono según el estado (expandido o colapsado)
        header_button.clicked.connect(lambda: self.toggle_panel_icon(header_button, content_widget))

        # Añadir el botón y el contenido al layout principal
        self.main_layout.addWidget(header_button)
        self.main_layout.addWidget(content_widget)

        # Iniciar la sección como oculta
        content_widget.setVisible(False)

    def display_objectives(self, project_instance, layout=None):
        # Usa el layout proporcionado o, si no se pasa ninguno, usa self.main_layout como predeterminado
        target_layout = layout if layout is not None else self.main_layout
        self.objectives_outer_frame = QFrame(self.central_widget)
        self.objectives_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección de objetivos dentro del marco exterior
        self.objectives_frame = QtWidgets.QWidget(self.objectives_outer_frame)
        self.objectives_layout = QVBoxLayout(self.objectives_frame)
        self.objectives_layout.setContentsMargins(20, 10, 20, 10)  # Reducido para ajustarse mejor al marco decorativo
        self.objectives_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Objetivos" y aplicar el estilo
        self.objectives_button = QtWidgets.QPushButton("Cargar Objetivos", self)
        self.objectives_button.setStyleSheet(button_style)
        self.objectives_button.clicked.connect(lambda: self.load_objectives_section(project_instance))
        self.objectives_layout.addWidget(self.objectives_button)

        # Agregar el layout de la sección de objetivos al marco exterior
        outer_layout = QVBoxLayout(self.objectives_outer_frame)
        outer_layout.addWidget(self.objectives_frame)
        outer_layout.setContentsMargins(15, 15, 15,
                                        15)  # Para dar un espacio entre el marco decorativo y el contenido interno

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Objetivos", self.objectives_outer_frame)
        self.add_tabPrincipal("Objetivos", self.objectives_outer_frame)

    # Método para cargar y mostrar la sección 'Objetivos' cuando se hace clic en el botón
    def load_objectives_section(self, project_instance):
        """
        Carga y muestra la sección 'Objetivos' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.objectives_button.setVisible(False)
        self.objectives_layout.removeWidget(self.objectives_button)
        self.objectives_button.deleteLater()

        # Obtener los objetivos del proyecto
        objectives = self.loader.get_objectives_for_project(project_instance)

        # Llamar a la función para mostrar la sección con las opciones de lista y tabla
        self.display_section(
            title="Objetivos",
            instances=objectives,
            get_func1=self.loader.get_objective_description,
            get_func2=self.loader.get_objective_related,
            get_func3=self.loader.invoke_void,
            get_func4=self.loader.invoke_void,
            column_titles=["Nombre", "Descripción", "Relaciones"],
            show_list=False,
            layout=self.objectives_layout  # Utilizar el layout del contenedor para la sección
        )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.objectives_frame.setVisible(True)

    # Método que muestra el botón inicial para cargar la sección de 'Marco Teórico'
    def display_marco_teorico(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Marco Teórico' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.marco_teorico_outer_frame = QFrame(self.central_widget)
        self.marco_teorico_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección de marco teórico dentro del marco exterior
        self.marco_teorico_container = QtWidgets.QWidget(self.marco_teorico_outer_frame)
        self.marco_teorico_layout = QVBoxLayout(self.marco_teorico_container)
        self.marco_teorico_layout.setContentsMargins(20, 10, 20, 10)
        self.marco_teorico_layout.setSpacing(10)

        # Crear el botón de "Cargar Marco Teórico" y añadirlo al contenedor
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        self.marco_teorico_button = QtWidgets.QPushButton("Cargar Marco Teórico")
        self.marco_teorico_button.setStyleSheet(button_style)
        self.marco_teorico_button.clicked.connect(lambda: self.load_marco_teorico_section(project_instance))
        self.marco_teorico_layout.addWidget(self.marco_teorico_button)

        # Agregar el layout de la sección de marco teórico al marco exterior
        outer_layout = QVBoxLayout(self.marco_teorico_outer_frame)
        outer_layout.addWidget(self.marco_teorico_container)
        outer_layout.setContentsMargins(15, 15, 15,
                                        15)  # Para dar un espacio entre el marco decorativo y el contenido interno

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Marco Teorico", self.marco_teorico_outer_frame)
        self.add_tabPrincipal("Marco Teorico", self.marco_teorico_outer_frame)

    # Método para cargar y mostrar la sección 'Marco Teórico' cuando se hace clic en el botón
    def load_marco_teorico_section(self, project_instance):
        """
        Carga y muestra la sección 'Marco Teórico' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.marco_teorico_button.setVisible(False)
        self.marco_teorico_layout.removeWidget(self.marco_teorico_button)
        self.marco_teorico_button.deleteLater()

        # Obtener las instancias de marco teórico para el proyecto
        marco_teorico_instances = self.loader.get_marco_teorico_for_project(project_instance)

        if marco_teorico_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Marcos Teoricos",
                instances=marco_teorico_instances,
                get_func1=self.loader.get_objective_autor,
                get_func2=self.loader.get_objective_value,
                get_func3=self.loader.get_objective_related,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Autor", "Valor", "Relaciones"],
                show_list=False,
                layout=self.marco_teorico_layout  # Utilizar el layout del contenedor para la sección
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.marco_teorico_container.setVisible(True)

    def display_bibliografia(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Bibliografía' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.bibliografia_outer_frame = QFrame(self.central_widget)
        self.bibliografia_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección de bibliografía dentro del marco exterior
        self.bibliografia_container = QtWidgets.QWidget(self.bibliografia_outer_frame)
        self.bibliografia_layout = QVBoxLayout(self.bibliografia_container)
        self.bibliografia_layout.setContentsMargins(20, 10, 20, 10)
        self.bibliografia_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Bibliografía" y añadirlo al contenedor
        self.bibliografia_button = QtWidgets.QPushButton("Cargar Bibliografía")
        self.bibliografia_button.setStyleSheet(button_style)
        self.bibliografia_button.clicked.connect(lambda: self.load_bibliografia_section(project_instance))
        self.bibliografia_layout.addWidget(self.bibliografia_button)

        # Agregar el layout de la sección de bibliografía al marco exterior
        outer_layout = QVBoxLayout(self.bibliografia_outer_frame)
        outer_layout.addWidget(self.bibliografia_container)
        outer_layout.setContentsMargins(15, 15, 15,
                                        15)  # Para dar un espacio entre el marco decorativo y el contenido interno

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Bibliografia", self.bibliografia_outer_frame)
        self.add_tabPrincipal("Bibliografia", self.bibliografia_outer_frame)

    def load_bibliografia_section(self, project_instance):
        """
        Carga y muestra la sección 'Marco Teórico' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.bibliografia_button.setVisible(False)
        self.bibliografia_layout.removeWidget(self.bibliografia_button)
        self.bibliografia_button.deleteLater()

        # Obtener las instancias de bibliografía para el proyecto
        bibliografia_instances = self.loader.get_bibliografia_for_project(project_instance)

        if bibliografia_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Bibliografía",
                instances=bibliografia_instances,
                get_func1=self.loader.get_objective_autor,
                get_func2=self.loader.get_objective_title,
                get_func3=self.loader.get_objective_related,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Autor", "Titulo", "Relaciones"],
                show_list=False,
                layout=self.bibliografia_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.bibliografia_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Estrategia Metodológica'
    def display_estrategia_metodologica(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Estrategia Metodológica' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.estrategia_outer_frame = QFrame(self.central_widget)
        self.estrategia_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección de estrategia metodológica dentro del marco exterior
        self.estrategia_container = QtWidgets.QWidget(self.estrategia_outer_frame)
        self.estrategia_layout = QVBoxLayout(self.estrategia_container)
        self.estrategia_layout.setContentsMargins(20, 10, 20, 10)
        self.estrategia_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Estrategia Metodológica" y añadirlo al contenedor
        self.estrategia_button = QtWidgets.QPushButton("Cargar Estrategia Metodológica")
        self.estrategia_button.setStyleSheet(button_style)
        self.estrategia_button.clicked.connect(lambda: self.load_estrategia_metodologica_section(project_instance))
        self.estrategia_layout.addWidget(self.estrategia_button)

        # Agregar el layout de la sección de estrategia metodológica al marco exterior
        outer_layout = QVBoxLayout(self.estrategia_outer_frame)
        outer_layout.addWidget(self.estrategia_container)
        outer_layout.setContentsMargins(15, 15, 15,
                                        15)  # Para dar un espacio entre el marco decorativo y el contenido interno

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Estrategia Metodológica", self.estrategia_outer_frame)
        self.add_tabPrincipal("Estrategia Metodológica", self.estrategia_outer_frame)

    # Método para cargar y mostrar la sección 'Estrategia Metodológica' cuando se hace clic en el botón
    def load_estrategia_metodologica_section(self, project_instance):
        """
        Carga y muestra la sección 'Estrategia Metodológica' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.estrategia_button.setVisible(False)
        self.estrategia_layout.removeWidget(self.estrategia_button)
        self.estrategia_button.deleteLater()

        # Obtener las instancias de estrategia metodológica para el proyecto
        estrategia_instances = self.loader.get_estrategia_metodologica_for_project(project_instance)

        if estrategia_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Estrategia Metodológica",
                instances=estrategia_instances,
                get_func1=self.loader.get_objective_objetive,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Objetivo", "Relaciones"],
                show_list=False,
                layout=self.estrategia_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.estrategia_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Técnica'
    def display_tecnica(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Técnica' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.tecnica_outer_frame = QFrame(self.central_widget)
        self.tecnica_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección de técnica dentro del marco exterior
        self.tecnica_container = QtWidgets.QWidget(self.tecnica_outer_frame)
        self.tecnica_layout = QVBoxLayout(self.tecnica_container)
        self.tecnica_layout.setContentsMargins(20, 10, 20, 10)
        self.tecnica_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Técnica" y añadirlo al contenedor
        self.tecnica_button = QtWidgets.QPushButton("Cargar Técnica")
        self.tecnica_button.setStyleSheet(button_style)
        self.tecnica_button.clicked.connect(lambda: self.load_tecnica_section(project_instance))
        self.tecnica_layout.addWidget(self.tecnica_button)

        # Agregar el layout de la sección de técnica al marco exterior
        outer_layout = QVBoxLayout(self.tecnica_outer_frame)
        outer_layout.addWidget(self.tecnica_container)
        outer_layout.setContentsMargins(15, 15, 15,
                                        15)  # Para dar un espacio entre el marco decorativo y el contenido interno

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Técnica", self.tecnica_outer_frame)
        self.add_tabPrincipal("Técnica", self.tecnica_outer_frame)

    # Método para cargar y mostrar la sección 'Técnica' cuando se hace clic en el botón
    def load_tecnica_section(self, project_instance):
        """
        Carga y muestra la sección 'Técnica' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.tecnica_button.setVisible(False)
        self.tecnica_layout.removeWidget(self.tecnica_button)
        self.tecnica_button.deleteLater()

        # Obtener las instancias de técnica para el proyecto
        tecnica_instances = self.loader.get_tecnica_for_project(project_instance)

        if tecnica_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Técnicas",
                instances=tecnica_instances,
                get_func1=self.loader.get_objective_objetive,
                get_func2=self.loader.get_objective_pauta,
                get_func3=self.loader.get_objective_nucleo,
                get_func4=self.loader.get_objective_related,
                column_titles=["Nombre", "Objetivo", "Pauta", "Nucleo", "Relaciones"],
                show_list=False,
                layout=self.tecnica_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.tecnica_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Sujeto u Objeto'
    def display_sujeto_u_objeto(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Sujeto u Objeto' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.sujeto_u_objeto_outer_frame = QFrame(self.central_widget)
        self.sujeto_u_objeto_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.sujeto_u_objeto_container = QtWidgets.QWidget(self.sujeto_u_objeto_outer_frame)
        self.sujeto_u_objeto_layout = QVBoxLayout(self.sujeto_u_objeto_container)
        self.sujeto_u_objeto_layout.setContentsMargins(20, 10, 20, 10)
        self.sujeto_u_objeto_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Sujeto u Objeto" y añadirlo al contenedor
        self.sujeto_u_objeto_button = QtWidgets.QPushButton("Cargar Sujeto u Objeto")
        self.sujeto_u_objeto_button.setStyleSheet(button_style)
        self.sujeto_u_objeto_button.clicked.connect(lambda: self.load_sujeto_u_objeto_section(project_instance))
        self.sujeto_u_objeto_layout.addWidget(self.sujeto_u_objeto_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.sujeto_u_objeto_outer_frame)
        outer_layout.addWidget(self.sujeto_u_objeto_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Sujeto u Objeto", self.sujeto_u_objeto_outer_frame)
        self.add_tabPrincipal("Sujeto u Objeto", self.sujeto_u_objeto_outer_frame)

    # Método para cargar y mostrar la sección 'Sujeto u Objeto' cuando se hace clic en el botón
    def load_sujeto_u_objeto_section(self, project_instance):
        """
        Carga y muestra la sección 'Sujeto u Objeto' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.sujeto_u_objeto_button.setVisible(False)
        self.sujeto_u_objeto_layout.removeWidget(self.sujeto_u_objeto_button)
        self.sujeto_u_objeto_button.deleteLater()

        # Obtener las instancias de sujeto u objeto para el proyecto
        sujeto_u_objeto_instances = self.loader.get_sujeto_u_objeto_for_project(project_instance)

        if sujeto_u_objeto_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Sujeto u Objeto",
                instances=sujeto_u_objeto_instances,
                get_func1=self.loader.get_objective_description,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Descripcion", "Relaciones"],
                show_list=False,
                layout=self.sujeto_u_objeto_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.sujeto_u_objeto_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Soporte'
    def display_soporte(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Soporte' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.soporte_outer_frame = QFrame(self.central_widget)
        self.soporte_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.soporte_container = QtWidgets.QWidget(self.soporte_outer_frame)
        self.soporte_layout = QVBoxLayout(self.soporte_container)
        self.soporte_layout.setContentsMargins(20, 10, 20, 10)
        self.soporte_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Soporte" y añadirlo al contenedor
        self.soporte_button = QtWidgets.QPushButton("Cargar Soporte")
        self.soporte_button.setStyleSheet(button_style)
        self.soporte_button.clicked.connect(lambda: self.load_soporte_section(project_instance))
        self.soporte_layout.addWidget(self.soporte_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.soporte_outer_frame)
        outer_layout.addWidget(self.soporte_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Soporte", self.soporte_outer_frame)
        self.add_tabPrincipal("Soporte", self.soporte_outer_frame)

    # Método para cargar y mostrar la sección 'Soporte' cuando se hace clic en el botón
    def load_soporte_section(self, project_instance):
        """
        Carga y muestra la sección 'Soporte' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.soporte_button.setVisible(False)
        self.soporte_layout.removeWidget(self.soporte_button)
        self.soporte_button.deleteLater()

        # Obtener las instancias de soporte para el proyecto
        soporte_instances = self.loader.get_soporte_for_project(project_instance)

        if soporte_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Soporte",
                instances=soporte_instances,
                get_func1=self.loader.get_objective_name,
                get_func2=self.loader.get_objective_location,
                get_func3=self.loader.get_objective_related,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Nombre Archivo", "Relaciones"],
                show_list=False,
                layout=self.soporte_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.soporte_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Registro'
    def display_registro(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Registro' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.registro_outer_frame = QFrame(self.central_widget)
        self.registro_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.registro_container = QtWidgets.QWidget(self.registro_outer_frame)
        self.registro_layout = QVBoxLayout(self.registro_container)
        self.registro_layout.setContentsMargins(20, 10, 20, 10)
        self.registro_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Registro" y añadirlo al contenedor
        self.registro_button = QtWidgets.QPushButton("Cargar Registro")
        self.registro_button.setStyleSheet(button_style)
        self.registro_button.clicked.connect(lambda: self.load_registro_section(project_instance))
        self.registro_layout.addWidget(self.registro_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.registro_outer_frame)
        outer_layout.addWidget(self.registro_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Registro", self.registro_outer_frame)
        self.add_tabPrincipal("Registro", self.registro_outer_frame)

    # Método para cargar y mostrar la sección 'Registro' cuando se hace clic en el botón
    def load_registro_section(self, project_instance):
        """
        Carga y muestra la sección 'Registro' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.registro_button.setVisible(False)
        self.registro_layout.removeWidget(self.registro_button)
        self.registro_button.deleteLater()

        # Obtener las instancias de registro para el proyecto
        registro_instances = self.loader.get_registro_for_project(project_instance)

        if registro_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Registros",
                instances=registro_instances,
                get_func1=self.loader.get_objective_value,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Valor", "Relaciones"],
                show_list=False,
                layout=self.registro_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.registro_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Información'
    def display_informacion(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Información' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.informacion_outer_frame = QFrame(self.central_widget)
        self.informacion_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.informacion_container = QtWidgets.QWidget(self.informacion_outer_frame)
        self.informacion_layout = QVBoxLayout(self.informacion_container)
        self.informacion_layout.setContentsMargins(20, 10, 20, 10)
        self.informacion_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Información" y añadirlo al contenedor
        self.informacion_button = QtWidgets.QPushButton("Cargar Información")
        self.informacion_button.setStyleSheet(button_style)
        self.informacion_button.clicked.connect(lambda: self.load_informacion_section(project_instance))
        self.informacion_layout.addWidget(self.informacion_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.informacion_outer_frame)
        outer_layout.addWidget(self.informacion_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Información", self.informacion_outer_frame)
        self.add_tabPrincipal("Información", self.informacion_outer_frame)

    # Método para cargar y mostrar la sección 'Información' cuando se hace clic en el botón
    def load_informacion_section(self, project_instance):
        """
        Carga y muestra la sección 'Información' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.informacion_button.setVisible(False)
        self.informacion_layout.removeWidget(self.informacion_button)
        self.informacion_button.deleteLater()

        # Obtener las instancias de información para el proyecto
        informacion_instances = self.loader.get_informacion_for_project(project_instance)

        if informacion_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Información",
                instances=informacion_instances,
                get_func1=self.loader.get_objective_value,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Valor", "Relaciones"],
                show_list=False,
                layout=self.informacion_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.informacion_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Metadatos'
    def display_metadatos(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Metadatos' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.metadatos_outer_frame = QFrame(self.central_widget)
        self.metadatos_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.metadatos_container = QtWidgets.QWidget(self.metadatos_outer_frame)
        self.metadatos_layout = QVBoxLayout(self.metadatos_container)
        self.metadatos_layout.setContentsMargins(20, 10, 20, 10)
        self.metadatos_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
                           QPushButton {
                               font-size: 16px;
                               font-weight: bold;
                               color: #333333;
                               background-color: #f9f9f9;
                               border: 1px solid #d3d3d3;
                               border-radius: 8px;
                               padding: 10px 20px;
                           }
                           QPushButton:hover {
                               background-color: #e0e0e0;
                           }
                           QPushButton:pressed {
                               background-color: #d0d0d0;
                           }
                       """

        # Crear el botón "Cargar Metadatos" y añadirlo al contenedor
        self.metadatos_button = QtWidgets.QPushButton("Cargar Metadatos")
        self.metadatos_button.setStyleSheet(button_style)
        self.metadatos_button.clicked.connect(lambda: self.load_metadatos_section(project_instance))
        self.metadatos_layout.addWidget(self.metadatos_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.metadatos_outer_frame)
        outer_layout.addWidget(self.metadatos_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Metadatos", self.metadatos_outer_frame)
        self.add_tabPrincipal("Metadatos", self.metadatos_outer_frame)

    # Método para cargar y mostrar la sección 'Metadatos' cuando se hace clic en el botón
    def load_metadatos_section(self, project_instance):
        """
        Carga y muestra la sección 'Metadatos' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.metadatos_button.setVisible(False)
        self.metadatos_layout.removeWidget(self.metadatos_button)
        self.metadatos_button.deleteLater()

        # Obtener las instancias de metadatos para el proyecto
        metadatos_instances = self.loader.get_metadatos_for_project(project_instance)

        if metadatos_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Metadatos",
                instances=metadatos_instances,
                get_func1=self.loader.get_objective_value,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Valor", "Relaciones"],
                show_list=False,
                layout=self.metadatos_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.metadatos_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Esquema de Clasificación Descriptiva'
    def display_esquema_clasificacion_descriptiva(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Esquema de Clasificación Descriptiva' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.esquema_clasificacion_descriptiva_outer_frame = QFrame(self.central_widget)
        self.esquema_clasificacion_descriptiva_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.esquema_clasificacion_descriptiva_container = QtWidgets.QWidget(
            self.esquema_clasificacion_descriptiva_outer_frame)
        self.esquema_clasificacion_descriptiva_layout = QVBoxLayout(self.esquema_clasificacion_descriptiva_container)
        self.esquema_clasificacion_descriptiva_layout.setContentsMargins(20, 10, 20, 10)
        self.esquema_clasificacion_descriptiva_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Esquema de Clasificación Descriptiva" y añadirlo al contenedor
        self.esquema_clasificacion_descriptiva_button = QtWidgets.QPushButton(
            "Cargar Esquema de Clasificación Descriptiva")
        self.esquema_clasificacion_descriptiva_button.setStyleSheet(button_style)
        self.esquema_clasificacion_descriptiva_button.clicked.connect(
            lambda: self.load_esquema_clasificacion_descriptiva_section(project_instance))
        self.esquema_clasificacion_descriptiva_layout.addWidget(self.esquema_clasificacion_descriptiva_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.esquema_clasificacion_descriptiva_outer_frame)
        outer_layout.addWidget(self.esquema_clasificacion_descriptiva_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Esquema de Clasificación Descriptiva",self.esquema_clasificacion_descriptiva_outer_frame)
        self.add_tabPrincipal("Esquema de Clasificación Descriptiva",
                              self.esquema_clasificacion_descriptiva_outer_frame)

    # Método para cargar y mostrar la sección 'Esquema de Clasificación Descriptiva' cuando se hace clic en el botón
    def load_esquema_clasificacion_descriptiva_section(self, project_instance):
        """
        Carga y muestra la sección 'Esquema de Clasificación Descriptiva' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.esquema_clasificacion_descriptiva_button.setVisible(False)
        self.esquema_clasificacion_descriptiva_layout.removeWidget(self.esquema_clasificacion_descriptiva_button)
        self.esquema_clasificacion_descriptiva_button.deleteLater()

        # Obtener las instancias de esquema de clasificación descriptiva para el proyecto
        esquema_descriptiva_instances = self.loader.get_esquema_clasificacion_descriptiva_for_project(project_instance)

        if esquema_descriptiva_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Categorías Descriptivas",
                instances=esquema_descriptiva_instances,
                get_func1=self.loader.get_objective_name,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Nombre de Categoría", "Relaciones"],
                show_list=False,
                layout=self.esquema_clasificacion_descriptiva_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.esquema_clasificacion_descriptiva_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Esquema de Clasificación Analítica'
    def display_esquema_clasificacion_analitica(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Esquema de Clasificación Analítica' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.esquema_clasificacion_analitica_outer_frame = QFrame(self.central_widget)
        self.esquema_clasificacion_analitica_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.esquema_clasificacion_analitica_container = QtWidgets.QWidget(
            self.esquema_clasificacion_analitica_outer_frame)
        self.esquema_clasificacion_analitica_layout = QVBoxLayout(self.esquema_clasificacion_analitica_container)
        self.esquema_clasificacion_analitica_layout.setContentsMargins(20, 10, 20, 10)
        self.esquema_clasificacion_analitica_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        # Crear el botón "Cargar Esquema de Clasificación Analítica" y añadirlo al contenedor
        self.esquema_clasificacion_analitica_button = QtWidgets.QPushButton("Cargar Esquema de Clasificación Analítica")
        self.esquema_clasificacion_analitica_button.setStyleSheet(button_style)
        self.esquema_clasificacion_analitica_button.clicked.connect(
            lambda: self.load_esquema_clasificacion_analitica_section(project_instance))
        self.esquema_clasificacion_analitica_layout.addWidget(self.esquema_clasificacion_analitica_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.esquema_clasificacion_analitica_outer_frame)
        outer_layout.addWidget(self.esquema_clasificacion_analitica_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Esquema de Clasificación Analítica",self.esquema_clasificacion_analitica_outer_frame)
        self.add_tabPrincipal("Esquema de Clasificación Analítica", self.esquema_clasificacion_analitica_outer_frame)

    # Método para cargar y mostrar la sección 'Esquema de Clasificación Analítica' cuando se hace clic en el botón
    def load_esquema_clasificacion_analitica_section(self, project_instance):
        """
        Carga y muestra la sección 'Esquema de Clasificación Analítica' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.esquema_clasificacion_analitica_button.setVisible(False)
        self.esquema_clasificacion_analitica_layout.removeWidget(self.esquema_clasificacion_analitica_button)
        self.esquema_clasificacion_analitica_button.deleteLater()

        # Obtener las instancias de esquema de clasificación analítica para el proyecto
        esquema_analitica_instances = self.loader.get_esquema_clasificacion_analitica_for_project(project_instance)

        if esquema_analitica_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Categorías Analíticas",
                instances=esquema_analitica_instances,
                get_func1=self.loader.get_objective_value,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Nombre de Categoría", "Relaciones"],
                show_list=False,
                layout=self.esquema_clasificacion_analitica_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.esquema_clasificacion_analitica_container.setVisible(True)

    # Método para mostrar el botón inicial que carga la sección de 'Reporte'
    def display_reporte(self, project_instance):
        """
        Crea un botón dentro de un contenedor que, al hacer clic, carga la sección de 'Reporte' en el lugar correcto.
        """

        # Crear un QFrame exterior para el estilo decorativo
        self.reporte_outer_frame = QFrame(self.central_widget)
        self.reporte_outer_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
        """)

        # Crear el contenedor principal de la sección dentro del marco exterior
        self.reporte_container = QtWidgets.QWidget(self.reporte_outer_frame)
        self.reporte_layout = QVBoxLayout(self.reporte_container)
        self.reporte_layout.setContentsMargins(20, 10, 20, 10)
        self.reporte_layout.setSpacing(10)

        # Definir el estilo para el botón
        button_style = """
                           QPushButton {
                               font-size: 16px;
                               font-weight: bold;
                               color: #333333;
                               background-color: #f9f9f9;
                               border: 1px solid #d3d3d3;
                               border-radius: 8px;
                               padding: 10px 20px;
                           }
                           QPushButton:hover {
                               background-color: #e0e0e0;
                           }
                           QPushButton:pressed {
                               background-color: #d0d0d0;
                           }
                       """
        # Crear el botón "Cargar Reporte" y añadirlo al contenedor
        self.reporte_button = QtWidgets.QPushButton("Cargar Reporte")
        self.reporte_button.setStyleSheet(button_style)
        self.reporte_button.clicked.connect(lambda: self.load_reporte_section(project_instance))
        self.reporte_layout.addWidget(self.reporte_button)

        # Agregar el layout de la sección al marco exterior
        outer_layout = QVBoxLayout(self.reporte_outer_frame)
        outer_layout.addWidget(self.reporte_container)
        outer_layout.setContentsMargins(15, 15, 15, 15)

        # Agregar el marco decorativo completo como panel expandible
        # self.add_expandable_panel("Reporte", self.reporte_outer_frame)
        self.add_tabPrincipal("Reporte", self.reporte_outer_frame)

    # Método para cargar y mostrar la sección 'Reporte' cuando se hace clic en el botón
    def load_reporte_section(self, project_instance):
        """
        Carga y muestra la sección 'Reporte' reemplazando el botón en el mismo contenedor.
        """
        # Ocultar y eliminar el botón
        self.reporte_button.setVisible(False)
        self.reporte_layout.removeWidget(self.reporte_button)
        self.reporte_button.deleteLater()

        # Obtener las instancias de reporte para el proyecto
        reporte_instances = self.loader.get_reporte_for_project(project_instance)

        if reporte_instances:
            # Llamar a la función para mostrar la sección con las opciones de lista y tabla
            self.display_section(
                title="Reporte",
                instances=reporte_instances,
                get_func1=self.loader.get_objective_value,
                get_func2=self.loader.get_objective_related,
                get_func3=self.loader.invoke_void,
                get_func4=self.loader.invoke_void,
                column_titles=["Nombre", "Nombre de Categoría", "Relaciones"],
                show_list=False,
                layout=self.reporte_layout  # Pasa el layout a display_section
            )

        # Asegurarse de que el contenedor se muestre con la nueva sección cargada
        self.reporte_container.setVisible(True)

    def add_tabPrincipal(self, title, content_widget):
        """
        Añade una nueva pestaña al QTabWidget.
        """
        self.tab_widgetPrincipal.addTab(content_widget, title)
        # Opcional: Aplica estilos al tab widget
        self.tab_widgetPrincipal.setStyleSheet("""
            QTabWidget::pane {
                border-top: 2px solid #666666;
            }
            QTabBar::tab {
                background: #444444;
                color: white;
                padding: 10px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background: #666666;
            }
            QTabBar::tab:hover {
                background: #555555;
            }
        """)



if __name__ == "__main__":
    try:
        logging.info("Iniciando la aplicación.")
        app = QtWidgets.QApplication([])
        window = OntologyViewer()
        window.show()
        logging.info("Ventana principal mostrada.")
        app.exec()
    except Exception as e:
        logging.critical("Ocurrió un error durante la ejecución de la aplicación.", exc_info=True)
        sys.exit(1)