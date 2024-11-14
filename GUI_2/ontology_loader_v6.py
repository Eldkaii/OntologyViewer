import shutil
import subprocess
import os

import rdflib
from rdflib import Graph
import PyQt6.QtWidgets


class OntologyLoader:
    def __init__(self):
        self.graph = None

    def load_rdf_file(self, file_name):
        """Carga el archivo RDF en el grafo."""
        self.graph = Graph()
        self.graph.parse(file_name)
        print(f"Archivo RDF '{file_name}' cargado correctamente.")



    def validate_ontology(self, file_name):
        jar_file = "razonador/validadorHermiT-jar-with-dependencies.jar"  # Ruta al archivo .jar
        command = ["java", "-jar", jar_file, file_name]

        try:
            res = subprocess.run(command, capture_output=True, text=True, check=True,creationflags=subprocess.CREATE_NO_WINDOW)

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


    def validate_and_infer_ontology(self, file_name,replace,justLoad, inference_options=None):

        base_name, ext = os.path.splitext(file_name)
        if justLoad:
            self.load_rdf_file(file_name)
            return True

        # Lista de opciones de inferencia válidas
        valid_inference_options = {
            "classAssertions": "classAssertions",
            "propertyAssertions": "propertyAssertions",
            "subClass": "subClass",
            "equivalentClass": "equivalentClass",
            "disjointClasses": "disjointClasses",
            "equivalentObjectProperty": "equivalentObjectProperty",
            "objectPropertyCharacteristic": "objectPropertyCharacteristic",
            "inverseObjectProperties": "inverseObjectProperties",
            "subObjectProperty": "subObjectProperty",
            "dataPropertyCharacteristic": "dataPropertyCharacteristic"
        }

        # Verificar qué opciones de inferencia se proporcionaron y construir la lista de argumentos
        selected_inferences = []
        if inference_options:
            for option in inference_options:
                if option in valid_inference_options:
                    selected_inferences.append(valid_inference_options[option])
                else:
                    print(f"Opción de inferencia no válida: {option}")

        if replace:
            # Preparación para la inferencia
            # Crear el nombre para la copia con el sufijo "_INF"
            # Obtener la carpeta y el nombre del archivo original
            folder_path = os.path.dirname(file_name)
            base_name = os.path.basename(file_name)
            copy_file_name = os.path.join(folder_path, f"{os.path.splitext(base_name)[0]}_INF.rdf")
            shutil.copy(file_name, copy_file_name)

            razonador = "razonador/razonadorHermiT-jar-with-dependencies_v5_no_topObjectProperty.jar"  # Ruta al archivo de inferencia
            # Construye el comando completo con los parámetros adicionales
            command_inference = ["java", "-jar", razonador, copy_file_name] + selected_inferences
        else:
            output_file = file_name
            razonador = "razonador/razonadorHermiT-jar-with-dependencies_v5_no_topObjectProperty.jar"  # Ruta al archivo de inferencia
            # Construye el comando completo con los parámetros adicionales
            command_inference = ["java", "-jar", razonador, file_name] + selected_inferences


        try:
            subprocess.run(command_inference, check=True,creationflags=subprocess.CREATE_NO_WINDOW)
            if replace:
                print(f"Ontología mejorada guardada en '{copy_file_name}'.")
                self.load_rdf_file(copy_file_name)

            else:
                print(f"Ontología mejorada guardada correctamente'.")
                self.load_rdf_file(file_name)




            return True
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar el archivo de inferencia .jar: {e}")
            return False

    def get_project_instances(self):
        """Retorna las instancias de la clase 'proyecto_de_investigacion'."""
        query = """
        SELECT ?project WHERE {
            ?project rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#proyecto_de_investigacion> .
        }
        """
        results = self.graph.query(query)
        return [str(row.project) for row in results]

    def get_investigators_for_project(self, project_instance):
        """Retorna los investigadores relacionados con un proyecto."""
        investigators_query = f"""
        SELECT ?investigator WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Es_participante> ?investigator .
        }}
        """
        return self.graph.query(investigators_query)

    def get_investigator_name(self, investigator_instance):
        """Retorna el atributo 'Nombre' de un investigador."""
        inv_name_query = f"""
        SELECT ?nombre WHERE {{
            <{investigator_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Nombre> ?nombre .
        }}
        """
        result = self.graph.query(inv_name_query)
        for row in result:
            return str(row.nombre)
        return None

    def get_objectives_for_project(self, project_instance):
        """Retorna los objetivos relacionados con un proyecto."""
        objectives_query = f"""
        SELECT ?objective WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_objetivo> ?objective .
        }}
        """
        return self.graph.query(objectives_query)


    def get_reformulaciones_objetivos_for_project(self, project_instance):
        """Retorna los objetivos relacionados con un proyecto."""
        objectives_query = f"""
        SELECT  ?objectiveRef ?reformulacion ?origen WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_objetivo> ?objectiveRef .
            ?reformulacion <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Destino_de_reformulacion> ?objectiveRef.
            ?origen <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Origen_de_reformulacion> ?reformulacion .
        }}
        """
        return self.graph.query(objectives_query)

    def get_properties_for_instance(self, instance_uri):
        """Obtiene las object properties y data properties de un named individual."""

        # Query para object properties (relaciones con otras instancias)
        object_properties_query = f"""
        SELECT ?property ?relatedInstance WHERE {{
            <{instance_uri}> ?property ?relatedInstance .
            FILTER (isIRI(?relatedInstance))
        }}
        """

        # Query para object properties (relaciones con otras instancias)
        object_properties2_query = f"""
        SELECT ?property ?relatedInstance WHERE {{
             ?relatedInstance ?property <{instance_uri}> .
            FILTER (isIRI(?relatedInstance))
        }}
        """

        # Query para data properties (valores literales como la descripción)
        data_properties_query = f"""
        SELECT ?property ?value WHERE {{
            <{instance_uri}> ?property ?value .
            FILTER (isLiteral(?value))
        }}
        """
        instance_name =  instance_uri.split("#")[-1]

        # Ejecutar las queries
        object_results = self.graph.query(object_properties_query)
        object2_results = self.graph.query(object_properties2_query)
        data_results = self.graph.query(data_properties_query)

        # Añadir las data properties (incluyendo la descripción)
        properties_info = "Propiedades:\n"
        for row in data_results:
            prop_name = row.property.split("#")[-1]
            value = row.value
            properties_info += f"     {prop_name}: {value}\n"

        # Preparar la información para mostrar
        properties_info += "\nRelaciones:\n"
        for row in object_results:
            prop_name = row.property.split("#")[-1]
            related_instance = row.relatedInstance.split("#")[-1]
            if prop_name != 'type':
                properties_info += f"     {instance_name} {prop_name} {related_instance}\n"
        for row in object2_results:
            prop_name = row.property.split("#")[-1]
            related_instance = row.relatedInstance.split("#")[-1]
            if prop_name != 'type':
                properties_info += f"{related_instance} {prop_name} {instance_name} \n"



        return properties_info

    def get_attributes_for_instance(self, instance):
        """
        Obtiene todos los atributos de una instancia dada.
        """
        if not instance:
            return []  # Devuelve una lista vacía si la instancia no es válida o está vacía

        # Asegurarse de que el URI esté rodeado de corchetes angulares
        instance_uri = f"<{instance}>"

        query = f"""
        SELECT ?property ?value WHERE {{
            {instance_uri} ?property ?value .
            FILTER(isLiteral(?value))  # Filtra solo las propiedades que tienen un valor literal
        }}
        """

        # Debug: Imprimir la consulta para ver si el URI está correctamente formateado
        print("SPARQL Query:", query)

        try:
            results = self.graph.query(query)
            attributes = [f"{str(row['property']).split('#')[-1]}: {row['value']}" for row in results]
            return attributes
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return []

    def get_marco_teorico_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'marco_teorico' relacionadas con el proyecto de investigación.
        """
        query = f"""
        SELECT ?marco_teorico WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_marco_teorico> ?marco_teorico .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_classes_for_instance(self, instance_uri):
        """
        Obtiene una lista de las clases a las que pertenece la instancia dada por instance_uri.
        """
        query = f"""
        SELECT ?class WHERE {{
            <{instance_uri}> rdf:type ?class .
            FILTER (?class != owl:NamedIndividual)
        }}
        """
        results = self.graph.query(query)
        classes = [str(result[0]).split('#')[-1] for result in results]
        return classes

    def get_bibliografia_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'Bibliografia' relacionadas con un proyecto de investigación.
        """
        query = f"""
        SELECT ?bibliografia WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_bibliografia> ?bibliografia .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_estrategia_metodologica_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'Estrategia metodologica' relacionadas con un proyecto de investigación.
        """
        query = f"""
        SELECT ?est_metodologica WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?est_metodologica .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_tecnica_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'tecnica' relacionadas con un proyecto de investigación.
        """
        query = f"""
        SELECT ?tecnica WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estrategia_metodologica .
            ?estrategia_metodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_techniques_for_estrategia(self, estrategia_instance):
        """
        Retorna las instancias de técnicas relacionadas con una estrategia metodológica.
        También devuelve la clase de cada técnica y su núcleo, aplicando la lógica de prioridad de clase:
        - Si tiene clase "observacion", mostrarla como "observacion".
        - Si tiene clase "entrevista", mostrarla como "entrevista".
        - Si tiene otra clase "XX", mostrarla como esa clase.
        - Si no tiene ninguna de las anteriores, mostrarla como "tecnica".
        """
        query = f"""
        SELECT ?tecnica ?tecnicaClass WHERE {{
            <{estrategia_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
            ?tecnica rdf:type ?tecnicaClass .
        }}
        """
        results = self.graph.query(query)
        techniques = {}

        for row in results:
            tecnica_uri = str(row.tecnica)
            tecnica_class = str(row.tecnicaClass).split("#")[-1]  # Obtener la clase de la técnica

            # Priorizar la clase según la lógica indicada
            if tecnica_uri not in techniques:
                techniques[tecnica_uri] = tecnica_class
            else:
                # Priorizar la clase "observacion", luego "entrevista", y finalmente cualquier otra clase
                current_class = techniques[tecnica_uri]
                if tecnica_class == "observacion":
                    techniques[tecnica_uri] = "observacion"
                elif tecnica_class == "entrevista" and current_class != "observacion":
                    techniques[tecnica_uri] = "entrevista"
                elif current_class not in ["observacion", "entrevista"]:
                    techniques[tecnica_uri] = tecnica_class

        # Si no tiene ninguna clase "observacion", "entrevista" o "XX", mostrar "tecnica"
        for tecnica_uri, tecnica_class in techniques.items():
            if tecnica_class not in ["observacion", "entrevista"]:
                techniques[tecnica_uri] = "tecnica"

        # Obtener el núcleo de las técnicas filtradas
        filtered_techniques = []
        for tecnica_uri, tecnica_class in techniques.items():
            nucleo = self.get_objective_nucleo(tecnica_uri)
            filtered_techniques.append((tecnica_uri, tecnica_class, nucleo))

        return filtered_techniques

    # Método para obtener instancias de 'sujeto_u_objeto'
    def get_sujeto_u_objeto_for_project(self, project_instance):
        query = f"""
          SELECT DISTINCT ?sujeto_u_objeto WHERE {{
              <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
              ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
              ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Se_aplica_en> ?sujeto_u_objeto . 
          }}
          """
        results = self.graph.query(query)
        return [row for row in results]

    # Método para obtener instancias de 'soporte'
    def get_soporte_for_project(self, project_instance):
        query = f"""
          SELECT DISTINCT ?soporte WHERE {{
              <{project_instance}> ?property ?related_instance .
              ?related_instance (<>|!<>)* ?registro .
              ?registro rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#registro> .
              ?registro <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Soportado_en> ?soporte .
          }}
          """
        results = self.graph.query(query)
        return [row for row in results]

        # Método para obtener instancias de 'registro'

    def get_registro_for_project(self, project_instance):

        # Primera consulta: registros relacionados con la instancia del proyecto a través de cualquier object property
        query = f"""
        SELECT DISTINCT ?registro WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?registro .
            ?registro rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#registro> .
        }}
        """
        # Ejecutar ambas consultas
        results = self.graph.query(query)
        return [row for row in results]

    def get_registro_especial_for_project(self, project_instance):

        # Segunda consulta: registros encontrados mediante la relación específica que genera el efecto de brillo
        query = f"""
        SELECT DISTINCT ?registro WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
            ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
            ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_tecnica_sobre_sujeto_u_objeto> ?tssuo . 
            ?tssuo <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Genera> ?registro .
        }}
        """
        # Ejecutar ambas consultas
        results = self.graph.query(query)
        return [row for row in results]

    def get_tecnicas_registros_for_project(self, project_instance):
        """
        Obtiene los URIs completos de técnicas y registros asociados para un proyecto dado.
        """
        query = f"""
        SELECT DISTINCT ?tecnica ?registro WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
            ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
            ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_tecnica_sobre_sujeto_u_objeto> ?tssuo . 
            ?tssuo <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Genera> ?registro .
        }}
        """
        results = self.graph.query(query)

        # Almacenar técnicas y registros sin formateo
        techniques_and_records = [(row['tecnica'], row['registro']) for row in results]

        return techniques_and_records

    def get_tecnicas_sujeto_o_objeto_for_project(self, project_instance):
        # Segunda consulta: registros encontrados mediante la relación específica que genera el efecto de brillo
        query = f"""
          SELECT DISTINCT ?tecnica ?sujeto WHERE {{
              <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
              ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
              ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_tecnica_sobre_sujeto_u_objeto> ?tssuo . 
              ?tssuo <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_sujeto_u_objeto> ?sujeto .
          }}
          """
        # Ejecutar ambas consultas
        results = self.graph.query(query)
        return [row for row in results]

    def get_tecnicas_registro_soporte_for_project(self, project_instance):
        """
        Obtiene técnicas, soportes y registros asociados para un proyecto dado, devolviendo todos los valores de URI completos.
        """
        query = f"""
        SELECT DISTINCT ?tecnica ?soporte ?registro WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
            ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
            ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_tecnica_sobre_sujeto_u_objeto> ?tssuo . 
            ?tssuo <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Genera> ?registro .
            ?registro <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Soportado_en> ?soporte .
        }}
        """
        results = self.graph.query(query)

        # Asegúrate de devolver los resultados como una lista de tuplas de URIs completos
        return [(str(row['tecnica']), str(row['soporte']), str(row['registro'])) for row in results]

    def get_informacion_especial_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'informacion' relacionadas con el proyecto dado.
        """
        query = f"""
                SELECT DISTINCT ?informacion WHERE {{
                    <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
                    ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
                    ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_tecnica_sobre_sujeto_u_objeto> ?tssuo . 
                    ?tssuo <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Genera> ?registro .
                    ?registro <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Se_interpreta> ?idur .
                    ?idur <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Relacionado_a_informacion> ?informacion .
                }}
                """
        results = self.graph.query(query)
        return [row for row in results]

    def get_informacion_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'informacion' relacionadas con el proyecto dado.
        """
        query = f"""
            SELECT DISTINCT ?informacion WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?informacion .
            ?informacion rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#informacion> .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_metadatos_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'Metadatos' relacionadas con el proyecto.
        """
        query = f"""
            SELECT DISTINCT ?metadato WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?metadato .
            ?metadato rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#metadatos> .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_esquema_clasificacion_descriptiva_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'esquema_de_clasificacion_descriptiva' relacionadas con el proyecto.
        """
        query = f"""
            SELECT DISTINCT ?esqDescriptiva WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?esqDescriptiva .
            ?esqDescriptiva rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#esquema_de_clasificacion_descriptivo> .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_esquema_clasificacion_descriptiva_registro_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'esquema_de_clasificacion_descriptiva' relacionadas con el proyecto.
        """
        query = f"""
            SELECT  ?esqDescriptiva ?registro WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?esqDescriptiva .
            ?esqDescriptiva rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#esquema_de_clasificacion_descriptivo> .
            ?idur <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_esquema_de_clasificacion_descriptiva> ?esqDescriptiva .
            ?registro <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Se_interpreta> ?idur .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_nucleos_guias_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'esquema_de_clasificacion_descriptiva' relacionadas con el proyecto.
        """
        query = f"""
            SELECT  ?tecnica ?preg WHERE {{
            <{project_instance}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Define> ?estMetodologica .
            ?estMetodologica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Aplica_una_o_varias> ?tecnica .
            ?tecnica rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#entrevista> .
            ?tecnica <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_pregunta> ?preg .


        }}
        """
        results = self.graph.query(query)
        return [row for row in results]


    def get_esquema_clasificacion_analitica_informacion_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'esquema_de_clasificacion_analitica' relacionadas con el proyecto.
        """
        query = f"""
            SELECT ?esqAnal ?informacion WHERE {{
            
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?esqAnal .
            ?esqAnal rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#esquema_de_clasificacion_analitico> .
            ?informacion <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tiene_esquema_de_clasificacion_analitica> ?esqAnal .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_esquema_clasificacion_analitica_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'esquema_de_clasificacion_analitica' relacionadas con el proyecto.
        """
        query = f"""
               SELECT DISTINCT ?esqAnal WHERE {{
               <{project_instance}> ?property ?related_instance .
               ?related_instance (<>|!<>)* ?esqAnal .
               ?esqAnal rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#esquema_de_clasificacion_analitico> .
           }}
           """
        results = self.graph.query(query)
        return [row for row in results]

    def get_reporte_for_project(self, project_instance):
        """
        Retorna las instancias de la clase 'reporte' relacionadas con el proyecto.
        """
        query = f"""
            SELECT DISTINCT ?reporte WHERE {{
            <{project_instance}> ?property ?related_instance .
            ?related_instance (<>|!<>)* ?reporte .
            ?reporte rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#reporte> .
        }}
        """
        results = self.graph.query(query)
        return [row for row in results]

    def get_objective_name(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?name WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Nombre> ?name .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.name)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_comment(self, instance_uri):
        """
        Retorna el valor de una instancia de 'objetivo'.

        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?com WHERE {{
            <{instance_uri}> <rdfs:comment> ?com .
        }}
        """

        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.com)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado
    def get_objective_value(self, instance_uri):
        """
        Retorna el valor de una instancia de 'objetivo'.

        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?value WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Valor> ?value .
        }}
        """

        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.value)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_description(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?desc WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Descripcion> ?desc .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.desc)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_title(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?title WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Titulo> ?title .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.title)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_autor(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?autor WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Autor> ?autor .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        if len(results) > 1:
            aut = ""
            for row in results:
                aut = aut + ", " + str(row.autor)
            return aut
        else:
            for row in results:
                return str(row.autor)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_type(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?tipo WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Tipo> ?tipo .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.tipo)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_location(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?location WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Ubicacion> ?location .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.location)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_objetive(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?obje WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Objetivo> ?obje .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.obje)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_pauta(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?pauta WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Pauta> ?pauta .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.pauta)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_nucleo(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?nucleo WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Nucleo> ?nucleo .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        for row in results:
            return str(row.nucleo)  # Retorna el valor como cadena

        return " "  # En caso de que no haya resultado

    def get_objective_conclusion(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
        SELECT ?conclusion WHERE {{
            <{instance_uri}> <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#Conclusion> ?conclusion .
        }}
        """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)
        if results:
            return [row for row in results]
        else:
            return " "

    def get_hallazgos_conclusiones_for_project(self, instance_uri):
        """
        instance_uri: URI de la instancia del objetivo
        """
        # Aquí agregarás la consulta SPARQL para obtener el valor del objetivo
        query = f"""
                SELECT DISTINCT ?reporte WHERE {{
                <{instance_uri}> ?property ?related_instance .
                ?related_instance (<>|!<>)* ?reporte .
                ?reporte rdf:type <http://www.semanticweb.org/emilio/ontologies/2024/5/untitled-ontology-27#reporte> .
                }}
                """
        # Ejecutar la consulta y devolver el valor
        results = self.graph.query(query)

        if results:
            return [row for row in results]
        else:
            return " "

    def invoke_void(self, instance_uri):
        """Invoca el poder antiguo de la nada misma"""
        return " "  # En caso de que no haya resultado

    def get_objective_related(self, instance_uri):
        """
        Retorna una cadena de texto que contiene las instancias relacionadas con la instancia dada mediante
        propiedades de objeto. Agrupa las instancias que comparten la misma propiedad, considerando si la
        instancia es el dominio o el rango, y reemplaza "_" por " ". Ignora la relación "rdf:type".

        instance_uri: URI de la instancia.
        """
        # Consulta SPARQL para obtener las relaciones donde la instancia es dominio (sujeto), ignorando "rdf:type"
        query_as_subject = f"""
        SELECT ?property ?related_instance WHERE {{
            <{instance_uri}> ?property ?related_instance .
            FILTER(isIRI(?related_instance) && ?property != rdf:type)
        }}
        """

        # Consulta SPARQL para obtener las relaciones donde la instancia es rango (objeto), ignorando "rdf:type"
        query_as_object = f"""
        SELECT ?property ?related_instance WHERE {{
            ?related_instance ?property <{instance_uri}> .
            FILTER(isIRI(?related_instance) && ?property != rdf:type)
        }}
        """

        # Ejecutar ambas consultas
        results_as_subject = self.graph.query(query_as_subject)
        results_as_object = self.graph.query(query_as_object)

        # Diccionario para agrupar instancias relacionadas por propiedad
        related_by_property_subject = {}  # Cuando la instancia es el sujeto
        related_by_property_object = {}  # Cuando la instancia es el objeto

        # Función auxiliar para agregar instancias al diccionario agrupado
        def add_related_instance(dictionary, property_name, related_instance):
            property_name = property_name.replace("_", " ")  # Reemplazar "_" por " "
            related_instance = related_instance.replace("_", " ")  # Reemplazar "_" por " "
            if property_name not in dictionary:
                dictionary[property_name] = []
            dictionary[property_name].append(related_instance)

        selected_instance = instance_uri.split("#")[-1].replace("_", " ")

        # Procesar los resultados donde la instancia es el sujeto (dominio)
        for row in results_as_subject:
            property_name = row.property.split("#")[-1]  # Extraer el nombre de la propiedad
            related_instance = row.related_instance.split("#")[-1]  # Extraer el nombre de la instancia relacionada
            add_related_instance(related_by_property_subject, property_name, related_instance)

        # Procesar los resultados donde la instancia es el objeto (rango)
        for row in results_as_object:
            property_name = row.property.split("#")[-1]
            related_instance = row.related_instance.split("#")[-1]
            add_related_instance(related_by_property_object, property_name, related_instance)

        # Preparar el string de resultados con el formato agrupado
        related_instances_str = ""

        # Formato cuando la instancia es el sujeto (dominio)
        for property_name, instances in related_by_property_subject.items():
            if len(instances) > 1:
                joined_instances = ", ".join(instances[:-1]) + " y " + instances[
                    -1]  # Concatenar con ", " y " y " para la última
            else:
                joined_instances = instances[0]  # Caso de una sola instancia, sin concatenación adicional
            related_instances_str += f"     <b>{selected_instance}</b> {property_name} {joined_instances}<br>"

        # Formato cuando la instancia es el objeto (rango)
        for property_name, instances in related_by_property_object.items():
            if len(instances) > 1:
                joined_instances = ", ".join(instances[:-1]) + " y " + instances[
                    -1]  # Concatenar con ", " y " y " para la última
            else:
                joined_instances = instances[0]  # Caso de una sola instancia, sin concatenación adicional
            related_instances_str += f"     {joined_instances} {property_name} <b>{selected_instance}</b><br>"

        # Si no se encontraron instancias relacionadas, devolver un mensaje por defecto
        if not related_instances_str.strip():  # Verificar si el string está vacío
            return "No se encontraron instancias relacionadas."

        return related_instances_str.strip()  # Devolver el string sin espacios adicionales








