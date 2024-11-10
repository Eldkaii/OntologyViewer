from rdflib import Graph, URIRef, Namespace, RDF, RDFS, OWL, Literal
import subprocess


# Definir el namespace general para el proyecto
ONTOLOGY_NAMESPACE = Namespace("http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#")


def cargar_ontologia(ruta):
    """Carga la ontología desde un archivo RDF y retorna el grafo RDF."""
    g = Graph()
    g.parse(ruta, format="xml")
    return g

def validate_ontology(file_name):
    jar_file = "razonador/validadorHermiT-jar-with-dependencies.jar"  # Ruta al archivo .jar
    command = ["java", "-jar", jar_file, file_name]

    try:
        res = subprocess.run(command, capture_output=True, text=True, check=True)

        # Captura la salida estándar del proceso (en caso de éxito)
        print(f"Validación exitosa: {res.stdout}")
        if res.stdout == 'La ontología es consistente.\n':
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        # Captura la salida de error del proceso (en caso de fallo)
        print(f"Error al ejecutar el archivo .jar: {e.stderr}")
        return False

def obtener_clases(g):
    """Obtiene todas las clases definidas en la ontología."""
    clases = []
    for s in g.subjects(RDF.type, OWL.Class):
        if isinstance(s, URIRef) and s.startswith(ONTOLOGY_NAMESPACE):
            clases.append(str(s).replace(str(ONTOLOGY_NAMESPACE), ""))
    return sorted(clases)


def obtener_relaciones(g):
    """Obtiene todas las propiedades de objeto (relaciones) definidas en la ontología."""
    relaciones = []
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        if isinstance(s, URIRef) and s.startswith(ONTOLOGY_NAMESPACE):
            relaciones.append(str(s).replace(str(ONTOLOGY_NAMESPACE), "").replace("_", " "))
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
