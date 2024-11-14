import os
import tempfile


from PyQt6.QtWidgets import (
    QMainWindow,  QComboBox,
    QMessageBox, QStackedWidget, QFormLayout, QSpacerItem, QSizePolicy, QCompleter
)
from PyQt6.QtCore import Qt
import utils
from utils import cargar_ontologia, obtener_clases, obtener_relaciones, obtener_atributos, guardar_instancia, \
    ONTOLOGY_NAMESPACE
from carga_xcel import *

class OntologyAppEditor(QMainWindow):
    def __init__(self, rdf_path):
        super().__init__()
        self.rdf_path = rdf_path
        self.setWindowTitle("Editor de Ontología Avanzado")
        self.setFixedSize(500, 600)
        self.force_close = False  # Bandera para forzar el cierre sin validar

        # Cargar y aplicar el archivo de estilo
        self.cargar_estilos()

        # Cargar la ontología desde la ruta proporcionada
        self.g = cargar_ontologia(rdf_path)

        # Cargar clases y relaciones
        self.clases = obtener_clases(self.g)
        self.relaciones = obtener_relaciones(self.g)

        # Configurar el QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Agregar las pantallas al QStackedWidget
        self.stacked_widget.addWidget(self.crear_menu_principal())  # Índice 0
        self.stacked_widget.addWidget(self.crear_vista_agregar_instancia())  # Índice 1
        self.stacked_widget.addWidget(self.crear_vista_agregar_relacion())  # Índice 2

        # Mostrar el menú principal al inicio
        self.stacked_widget.setCurrentIndex(0)

    def crear_menu_principal(self):
        """Crea el menú principal para seleccionar entre agregar instancia o relación."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Seleccione una opción")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Botón para agregar instancia
        add_instance_button = QPushButton("Agregar Instancia")
        add_instance_button.setFixedHeight(40)
        add_instance_button.clicked.connect(self.mostrar_agregar_instancia)
        layout.addWidget(add_instance_button)

        # Botón para agregar relación
        add_relation_button = QPushButton("Agregar Relación")
        add_relation_button.setFixedHeight(40)
        add_relation_button.clicked.connect(self.mostrar_agregar_relacion)
        layout.addWidget(add_relation_button)

        # Botón para regresar al menú principal con confirmación
        def confirmar_y_cerrar():
            # Crear el cuadro de diálogo de confirmación
            mensaje_confirmacion = QMessageBox()
            mensaje_confirmacion.setWindowTitle("Confirmación")
            mensaje_confirmacion.setText("¿Estás seguro de que deseas cerrar sin guardar?")
            mensaje_confirmacion.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            mensaje_confirmacion.setDefaultButton(QMessageBox.StandardButton.No)

            # Mostrar el cuadro de diálogo y verificar la respuesta
            respuesta = mensaje_confirmacion.exec()

            # Si el usuario confirma, activar la bandera y cerrar la ventana
            if respuesta == QMessageBox.StandardButton.Yes:
                self.force_close = True  # Activa la bandera para omitir la validación
                self.close()  # Cierra la ventana actual
        cerrar_sin_guardar_button = QPushButton("Cerrar sin guardar")
        cerrar_sin_guardar_button.setFixedHeight(40)
        cerrar_sin_guardar_button.clicked.connect(confirmar_y_cerrar)

        layout.addWidget(cerrar_sin_guardar_button)



        # Crear el widget del menú principal
        menu_widget = QWidget()
        menu_widget.setLayout(layout)
        return menu_widget


    def crear_vista_agregar_relacion(self):
        """Crea la interfaz para agregar una relación entre instancias usando comboboxes con filtrado."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ComboBox para la relación
        layout.addWidget(QLabel("Relación:"))
        self.relation_combo = QComboBox()
        self.relation_combo.addItems(self.relaciones)
        layout.addWidget(self.relation_combo)

        # ComboBox para la instancia de origen
        layout.addWidget(QLabel("Instancia de Origen:"))
        self.source_instance_combo = QComboBox()
        self.source_instance_combo.setEditable(True)
        source_completer = QCompleter(self.obtener_nombres_instancias(), self)
        source_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.source_instance_combo.setCompleter(source_completer)
        layout.addWidget(self.source_instance_combo)

        # ComboBox para la instancia de destino
        layout.addWidget(QLabel("Instancia de Destino:"))
        self.target_instance_combo = QComboBox()
        self.target_instance_combo.setEditable(True)
        target_completer = QCompleter(self.obtener_nombres_instancias(), self)
        target_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.target_instance_combo.setCompleter(target_completer)
        layout.addWidget(self.target_instance_combo)

        # Botón para guardar la relación
        save_relation_button = QPushButton("Guardar Relación")
        save_relation_button.setObjectName("actionButton")
        save_relation_button.setFixedHeight(40)
        save_relation_button.clicked.connect(self.agregar_relacion)
        layout.addWidget(save_relation_button)

        # Botón para regresar al menú principal
        back_button2 = QPushButton("Volver")
        back_button2.setFixedHeight(40)
        back_button2.clicked.connect(self.mostrar_menu_principal)  # Conecta al menú principal
        layout.addWidget(back_button2)








        # Crear el widget de agregar relación
        relation_widget = QWidget()
        relation_widget.setLayout(layout)
        return relation_widget

    def cargar_estilos(self):
        """Carga y aplica el archivo de estilo QSS."""
        try:
            with open("style.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Archivo style.qss no encontrado. Asegúrate de que el archivo esté en la misma carpeta que este script.")

    def mostrar_menu_principal(self):
        """Muestra el menú principal."""
        self.stacked_widget.setCurrentIndex(0)

    def mostrar_agregar_instancia(self):
        """Muestra la vista para agregar una nueva instancia."""
        self.stacked_widget.setCurrentIndex(1)
        self.mostrar_atributos_clase()

    def mostrar_agregar_relacion(self):
        """Muestra la vista para agregar una relación entre instancias."""
        self.stacked_widget.setCurrentIndex(2)

    def crear_vista_agregar_instancia(self):
        """Crea la interfaz para agregar una nueva instancia."""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título y selección de clase
        layout.addWidget(QLabel("Clase:"))
        self.class_combo = QComboBox()
        self.class_combo.addItems(self.clases)
        self.class_combo.currentIndexChanged.connect(self.mostrar_atributos_clase)
        layout.addWidget(self.class_combo)

        # Campo de entrada para el nombre de la instancia
        layout.addWidget(QLabel("Nombre de la Instancia:"))
        self.instance_input = QLineEdit()
        layout.addWidget(self.instance_input)

        # Contenedor para los atributos dinámicos
        self.atributos_layout = QFormLayout()
        layout.addLayout(self.atributos_layout)

        # Espaciador para empujar los botones hacia el fondo
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Botón para guardar la instancia
        save_instance_button = QPushButton("Guardar Instancia")
        save_instance_button.setObjectName("actionButton")
        save_instance_button.setFixedHeight(40)
        save_instance_button.clicked.connect(self.agregar_instancia)
        layout.addWidget(save_instance_button)

        # Botón para regresar al menú principal
        back_button = QPushButton("Volver")
        back_button.setFixedHeight(40)
        back_button.clicked.connect(self.mostrar_menu_principal)
        layout.addWidget(back_button)

        # Crear el widget de agregar instancia
        instance_widget = QWidget()
        instance_widget.setLayout(layout)
        return instance_widget

    def mostrar_atributos_clase(self):
        """Muestra los atributos de la clase seleccionada para que el usuario los complete."""
        # Limpiar el layout de atributos anteriores
        for i in reversed(range(self.atributos_layout.count())):
            widget = self.atributos_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Obtener los atributos de la clase seleccionada
        clase = self.class_combo.currentText()
        atributos = obtener_atributos(self.g, clase)

        # Crear campos de entrada para cada atributo
        self.atributo_inputs = {}
        for atributo in atributos:
            label = QLabel(atributo)
            input_field = QLineEdit()
            self.atributos_layout.addRow(label, input_field)
            self.atributo_inputs[atributo] = input_field

    def obtener_nombres_instancias(self):
        """Devuelve una lista con los nombres únicos de todas las instancias en el grafo RDF."""
        nombres_instancias = set()  # Usar un set para eliminar duplicados
        for s in self.g.subjects():
            if (s, RDF.type, URIRef("http://www.w3.org/2002/07/owl#NamedIndividual")) in self.g:
                nombre = str(s).replace(str(ONTOLOGY_NAMESPACE), "")
                nombres_instancias.add(nombre)  # Agregar al set en lugar de una lista
        return sorted(nombres_instancias)  # Convertir a lista ordenada

    def agregar_instancia(self):
        """Agrega una instancia a la ontología con sus atributos."""
        clase = self.class_combo.currentText()
        nombre_instancia = self.instance_input.text().strip().replace(" ", "_")

        if clase and nombre_instancia:
            atributos = {atributo: input_field.text().strip() for atributo, input_field in self.atributo_inputs.items()}
            guardar_instancia(self.g, clase, nombre_instancia, atributos)
            QMessageBox.information(self, "Éxito", f"Instancia '{nombre_instancia}' agregada a la clase '{clase}' con atributos.")
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona la clase e ingresa el nombre de la instancia.")

    def agregar_relacion(self):
        """Agrega una relación entre dos instancias en la ontología."""
        instancia_origen = self.source_instance_combo.currentText().strip()
        relacion = self.relation_combo.currentText().replace(" ", "_")
        instancia_destino = self.target_instance_combo.currentText().strip()

        if instancia_origen and relacion and instancia_destino:
            instancia_origen_uri = URIRef(ONTOLOGY_NAMESPACE + instancia_origen)
            relacion_uri = URIRef(ONTOLOGY_NAMESPACE + relacion)
            instancia_destino_uri = URIRef(ONTOLOGY_NAMESPACE + instancia_destino)
            self.g.add((instancia_origen_uri, relacion_uri, instancia_destino_uri))
            QMessageBox.information(self, "Éxito",
                                    f"Relacion '{relacion_uri}' agregada.")

        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, completa todos los campos para agregar una relación.")

    # Modificar el closeEvent para verificar la bandera
    def closeEvent(self, event):
        """Valida la ontología en un archivo temporal antes de guardar en el archivo principal."""
        if self.force_close:
            # Si la bandera está activa, omitir validación y solo cerrar
            event.accept()  # Cierra la ventana sin validación
            return

        # Crear un archivo temporal para la validación
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".rdf")
        temp_path = temp_file.name  # Ruta del archivo temporal
        temp_file.close()  # Cerrar el archivo temporal para que pueda ser usado por la validación

        # Guardar los cambios en el archivo temporal
        self.g.serialize(destination=temp_path, format="xml")

        # Validar la ontología en el archivo temporal usando la ruta del archivo
        if utils.validate_ontology(temp_path):  # Usar temp_path en lugar de temp_file
            # Si la validación es exitosa, guardar en el archivo principal
            self.g.serialize(destination=self.rdf_path, format="xml")
            QMessageBox.information(self, "Guardado", "Cambios guardados en el archivo RDF.")
            event.accept()  # Cerrar la ventana
        else:
            # Si la validación falla, mostrar advertencia y cancelar el cierre
            QMessageBox.warning(self, "Error de Validación",
                                "La ontología no es válida. No se guardarán los cambios.")
            event.accept()  # Cerrar la ventana

        # Eliminar el archivo temporal
        os.remove(temp_path)
