
from ui_components import OntologyApp  # Importar la interfaz de usuario desde el archivo ui_components
import sys
from PyQt6.QtWidgets import QApplication


def iniciar_app(ruta_rdf):
    app = QApplication(sys.argv)
    window = OntologyApp(ruta_rdf)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Editor de Ontología RDF")
    parser.add_argument("rdf_path", help="Ruta al archivo RDF")
    args = parser.parse_args()
    iniciar_app(args.rdf_path)
