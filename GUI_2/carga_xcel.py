import shutil

import pandas as pd
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL, XSD
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QLabel, QHBoxLayout, QCheckBox, QFileDialog, QDialog, QTextEdit, QWidget, QFrame, QGridLayout,QLineEdit,QPushButton,QTabWidget
import re
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


# Función para reemplazar espacios en nombres con guiones bajos
def replace_spaces(text):
    if isinstance(text, str):  # Solo procesar si es una cadena
        return re.sub(r'\s+', '_', text.strip())
    return ""  # Retornar cadena vacía si no es una cadena válida


def load_excel_and_populate_ontology(self):
    # Selección del archivo Excel

    # Crear un cuadro de mensaje con dos opciones
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
    msg_box.setWindowTitle("ARCHIVO EXCEL")
    msg_box.setText("Seleccione una opción:")

    # Añadir botones personalizados
    cargar_btn = msg_box.addButton("Cargar Excel", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
    descargar_btn = msg_box.addButton("Descargar Excel de ejemplo", QtWidgets.QMessageBox.ButtonRole.ActionRole)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Cancel)

    # Ejecutar el cuadro de mensaje y capturar la respuesta
    msg_box.exec()

    # Verificar qué botón se seleccionó
    if msg_box.clickedButton() == cargar_btn:
        # Continuar con la carga del archivo Excel
        # Aquí puedes añadir la lógica para seleccionar el archivo y cargarlo
        file_dialog = QtWidgets.QFileDialog()
        excel_path, _ = QFileDialog.getOpenFileName(self, "Elegir EXCEL con la ontología", "", "Excel (*.xlsx);;All Files (*)")
        if excel_path:
            # Procesar el archivo seleccionado (continuar con la lógica de carga)
            print(f"Archivo seleccionado: {excel_path}")
        if not excel_path:
            print("No se seleccionó un archivo Excel.")
            return

    elif msg_box.clickedButton() == descargar_btn:
        # Descargar el archivo Excel de ejemplo
        example_file_path = Path("base_documents/carga_ontologia_ejemplo.xlsx")
        if example_file_path.exists():
            # Seleccionar ruta de destino
            save_dialog = QtWidgets.QFileDialog()
            save_path, _ = save_dialog.getSaveFileName(None, "Guardar archivo de ejemplo", "ontologia_ejemplo.xlsx",
                                                       "Excel Files (*.xlsx)")
            if save_path:
                # Copiar el archivo a la ubicación seleccionada
                shutil.copy(example_file_path, save_path)
                QtWidgets.QMessageBox.information(None, "Descarga completa",
                                                  "El archivo de ejemplo ha sido descargado con éxito.")

            return
        else:
            QtWidgets.QMessageBox.warning(None, "Error", "El archivo de ejemplo no se encontró.")
            return





    # Crear un cuadro de mensaje con dos opciones
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
    msg_box.setWindowTitle("Archivo RDF")
    msg_box.setText("¿Desea cargar la ontología en un repositorio propio o usar un repositorio nuevo?")

    # Añadir botones personalizados
    propio_btn = msg_box.addButton("Repositorio propio", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
    nuevo_btn = msg_box.addButton("Repositorio nuevo", QtWidgets.QMessageBox.ButtonRole.ActionRole)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Cancel)

    # Ejecutar el cuadro de mensaje y capturar la respuesta
    msg_box.exec()

    # Variable para almacenar la ruta seleccionada
    selected_file_path = None

    # Verificar qué botón se seleccionó
    if msg_box.clickedButton() == propio_btn:
        # Continuar con la lógica para cargar archivo propio
        file_dialog = QtWidgets.QFileDialog()
        ontology_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo RDF", "", "RDF Files (*.rdf);;All Files (*)")
        if ontology_path:
            # Guardar la ruta del archivo seleccionado
            selected_file_path = ontology_path
            print(f"Archivo propio seleccionado: {selected_file_path}")

    elif msg_box.clickedButton() == nuevo_btn:
        # Descargar el archivo RDF de ejemplo
        example_file_path = Path("base_documents/ont_investigacion_cualitativa_VACIO.rdf")
        if example_file_path.exists():
            # Seleccionar ruta de destino
            save_dialog = QtWidgets.QFileDialog()
            save_path, _ = save_dialog.getSaveFileName(None, "Guardar repositorio nuevo", "ontologia_nueva.rdf",
                                                       "RDF Files (*.rdf)")
            if save_path:
                # Copiar el archivo de ejemplo a la ubicación seleccionada
                shutil.copy(example_file_path, save_path)
                selected_file_path = save_path
                QtWidgets.QMessageBox.information(None, "Descarga completa",
                                                  "El repositorio nuevo ha sido guardado con éxito.")
            else:
                QtWidgets.QMessageBox.warning(None, "Cancelado",
                                              "No se seleccionó ninguna ruta para guardar el archivo.")
                return
        else:
            QtWidgets.QMessageBox.warning(None, "Error", "El archivo de repositorio nuevo no se encontró.")
            return

    if not selected_file_path or not excel_path:
        return
    try:
        # Cargar la ontología base
        g = Graph()
        g.parse(selected_file_path)
    except Exception as e:
        logging.error(e)
        return

    # Definir el namespace de la ontología
    namespace_uri = "http://www.semanticweb.org/tesis_inv_cualitativa#"
    ns = Namespace(namespace_uri)
    g.bind("ns", ns)

    # Obtener todas las clases y relaciones de la ontología, reemplazando espacios por "_"
    ontology_classes = {replace_spaces(str(c).split("#")[-1]) for c in g.subjects(RDF.type, OWL.Class)}
    ontology_relations = {replace_spaces(str(p).split("#")[-1]) for p in g.subjects(RDF.type, OWL.ObjectProperty)}

    # Cargar el archivo de Excel
    xls = pd.ExcelFile(excel_path)
    main_sheet = xls.parse(0)  # Primera hoja: clases, instancias y data properties
    relations_sheet = xls.parse(1)  # Segunda hoja: relaciones

    # Verificar clases en la primera hoja del Excel
    invalid_classes = {replace_spaces(row["Clase"]) for _, row in main_sheet.iterrows() if replace_spaces(row["Clase"]) not in ontology_classes}
    if invalid_classes:
        print("Las siguientes clases del Excel no existen en la ontología:", invalid_classes)
        return  # Terminar si hay clases inválidas

    # Verificar relaciones en la segunda hoja del Excel
    relations_sheet.columns = [replace_spaces(col) for col in relations_sheet.columns]
    invalid_relations = {replace_spaces(row["Relacion"]) for _, row in relations_sheet.iterrows() if replace_spaces(row["Relacion"]) not in ontology_relations}
    if invalid_relations:
        print("Las siguientes relaciones del Excel no existen en la ontología:", invalid_relations)
        return  # Terminar si hay relaciones inválidas

    # Crear instancias y propiedades de datos en base a la primera hoja
    for _, row in main_sheet.iterrows():
        class_name = replace_spaces(row["Clase"])
        instance_name = replace_spaces(row["Instancia"])

        if class_name and instance_name:  # Solo añadir si ambos nombres son válidos
            class_uri = ns[class_name]
            instance_uri = ns[instance_name]

            # Agregar la instancia y su tipo (clase)
            g.add((instance_uri, RDF.type, OWL.NamedIndividual))
            g.add((instance_uri, RDF.type, class_uri))

            # Agregar data properties para la instancia
            for prop_name, value in row[2:].items():  # Ignorar las dos primeras columnas (Clase, Instancia)
                if pd.notna(value):  # Si hay un valor, se agrega como data property
                    prop_uri = ns[replace_spaces(prop_name)]
                    g.add((instance_uri, prop_uri, Literal(value)))

    # Agregar relaciones en base a la segunda hoja
    for _, row in relations_sheet.iterrows():
        subject_instance = ns[replace_spaces(row["Dominio"])]
        relation_uri = ns[replace_spaces(row["Relacion"])]
        object_instance = ns[replace_spaces(row["Rango"])]

        if subject_instance and relation_uri and object_instance:  # Añadir solo si todos son válidos
            g.add((subject_instance, relation_uri, object_instance))

    # Guardar el grafo actualizado en el archivo RDF seleccionado

    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
    try:
        g.serialize(destination=selected_file_path, format="xml")
        # Crear un cuadro de mensaje de información

        msg_box.setWindowTitle("CARGA EXITOSA")
        msg_box.setText(f"Ontología con instancias y propiedades de datos guardada exitosamente en {selected_file_path}")

    except Exception as e:
        logging.error(e)
        msg_box.setWindowTitle("CARGA FALLIDA")
        print(e.args)
        msg_box.setText(e.args)

    msg_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
    msg_box.exec()