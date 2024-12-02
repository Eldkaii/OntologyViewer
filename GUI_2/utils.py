from rdflib import Graph, URIRef, Namespace, RDF, RDFS, OWL, Literal
import subprocess
import os
import logging

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


# Definir el namespace general para el proyecto
ONTOLOGY_NAMESPACE = Namespace("http://www.semanticweb.org/tesis_inv_cualitativa#")


def cargar_ontologia(ruta):
    """Carga la ontología desde un archivo RDF y retorna el grafo RDF."""
    g = Graph()
    g.parse(ruta, format="xml")
    return g

def validate_ontology(file_name):
    # Ruta al ejecutable de Java portable
    java_path = os.path.join("portableHJDK_64_17_0_11", "CommonFiles", "OpenJDKJRE64", "bin", "java.exe")
    jar_file = os.path.join("razonador", "validadorHermiT-jar-with-dependencies.jar")

    # Verificar que las rutas existen
    if not os.path.exists(java_path):
        logging.error(f"Error: No se encontró el ejecutable de Java en {java_path}")
        print(f"Error: No se encontró el ejecutable de Java en {java_path}")
        return False
    if not os.path.exists(jar_file):
        logging.error(f"Error: No se encontró el archivo .jar en {jar_file}")
        print(f"Error: No se encontró el archivo .jar en {jar_file}")
        return False

    try:
        # Comando para ejecutar el JAR usando el Java portable
        command = [java_path, "-jar", jar_file, file_name]
        print(f"Ejecutando: {' '.join(command)}")

        # Ejecutar el comando
        res = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Salida estándar: {res.stdout}")

        # Verificar el resultado
        if "La ontología es consistente" in res.stdout:
            print("La ontología es consistente.")
            return True
        else:
            print("La ontología no es consistente.")
            return False

    except subprocess.CalledProcessError as e:
        logging.critical(e)
        print(f"Error al ejecutar Java: {e.stderr}")
        return False

    except Exception as e:
        logging.critical(e)
        print(f"Error inesperado: {e}")
        return False

def obtener_clases(g):
    """Obtiene todas las clases definidas en la ontología, eliminando duplicados."""
    clases = set()
    for s in g.subjects(RDF.type, OWL.Class):
        if isinstance(s, URIRef) and s.startswith(ONTOLOGY_NAMESPACE):
            clases.add(str(s).replace(str(ONTOLOGY_NAMESPACE), ""))
    return sorted(clases)



def obtener_relaciones(g):
    """Obtiene todas las propiedades de objeto (relaciones) definidas en la ontología, eliminando duplicados."""
    relaciones = set()
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        if isinstance(s, URIRef) and s.startswith(ONTOLOGY_NAMESPACE):
            relaciones.add(str(s).replace(str(ONTOLOGY_NAMESPACE), "").replace("_", " "))
    return sorted(relaciones)


def obtener_atributos(g, clase):
    """Obtiene todos los atributos (data properties) asociados a una clase, considerando uniones de dominios."""
    atributos = []
    clase_uri = URIRef(ONTOLOGY_NAMESPACE + clase)

    for atributo in g.subjects(RDFS.domain, None):
        # Verificar si el dominio es directamente la clase
        if (atributo, RDFS.domain, clase_uri) in g and (atributo, RDF.type, OWL.DatatypeProperty) in g:
            atributos.append(str(atributo).replace(str(ONTOLOGY_NAMESPACE), "").replace("_", " "))
            continue

        # Verificar si el dominio es una unión de clases
        for union in g.objects(atributo, RDFS.domain):
            if (union, RDF.type, OWL.Class) in g and (union, OWL.unionOf, None) in g:
                for clase_en_union in g.objects(union, OWL.unionOf):
                    # Iterar sobre los miembros de la unión
                    for member in g.items(clase_en_union):
                        if member == clase_uri:
                            atributos.append(str(atributo).replace(str(ONTOLOGY_NAMESPACE), "").replace("_", " "))
                            break
    return sorted(atributos)



def guardar_instancia(g, clase, nombre_instancia, atributos):
    """Guarda una nueva instancia con sus atributos en el grafo RDF."""
    instancia_uri = URIRef(ONTOLOGY_NAMESPACE + nombre_instancia)
    clase_uri = URIRef(ONTOLOGY_NAMESPACE + clase)
    g.add((instancia_uri, RDF.type, clase_uri))

    for atributo, valor in atributos.items():
        if valor:
            atributo_uri = URIRef(ONTOLOGY_NAMESPACE + atributo.replace(" ", "_"))
            g.add((instancia_uri, atributo_uri, Literal(valor)))
    return instancia_uri
