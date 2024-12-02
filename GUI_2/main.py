from PyQt6.QtWidgets import QApplication

from ui_components import OntologyAppEditor
import logging, os

# 1. Generar la ruta para el archivo de log en %APPDATA%
log_path = os.path.join(os.getenv("APPDATA"), "Ontology Viewer", "log_debug.txt")

# 2. Crear el directorio si no existe
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# 3. Configurar logging para usar la nueva ubicación del archivo
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Modificación de iniciar_app para que solo reciba la ruta y cree la ventana
def iniciar_app(ruta_rdf):
    try:
        # Crea y muestra la ventana principal
        window = OntologyAppEditor(ruta_rdf)
        window.show()
        return window  # Devuelve la ventana para mantener referencia en la aplicación principal
    except Exception as e:
        logging.error(e)


# Solo ejecuta el siguiente bloque si se llama este script de forma independiente
if __name__ == "__main__":
    import argparse
    import sys

    # Ejecuta QApplication si este script se ejecuta directamente
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description="Editor de Ontología RDF")
    parser.add_argument("rdf_path", help="Ruta al archivo RDF")
    args = parser.parse_args()

    # Llama a iniciar_app y mantiene la ventana abierta
    window = iniciar_app(args.rdf_path)
    sys.exit(app.exec())  # Solo se cierra la aplicación en este caso