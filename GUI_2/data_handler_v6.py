import logging
#
# from rdflib import Graph
# import logging
#
# # Configurar el logging
# logging.basicConfig(
#     filename='log_debug.txt',  # Nombre del archivo de log
#     level=logging.INFO,  # Nivel de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
#     format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del log
#     datefmt='%Y-%m-%d %H:%M:%S'  # Formato de fecha y hora
# )
#
# class DataHandler:
#     def __init__(self):
#         self.graph = None
#
#     def load_rdf_file(self, file_name):
#         """Carga el archivo RDF en el grafo."""
#         try:
#             self.graph = Graph()
#             self.graph.parse(file_name)
#             print(f"Archivo RDF '{file_name}' cargado correctamente.")
#         except Exception as e:
#             logging.info(e)
#
#     def get_project_instances(self):
#         """Retorna las instancias de la clase 'proyecto_de_investigacion'."""
#         query = """
#         SELECT ?project WHERE {
#             ?project rdf:type <http://www.semanticweb.org/tesis_inv_cualitativa#proyecto_de_investigacion> .
#         }
#         """
#         results = self.graph.query(query)
#         return [str(row.project) for row in results]
#
#     def get_investigators_for_project(self, project_instance):
#         """Retorna los investigadores relacionados con un proyecto."""
#         investigators_query = f"""
#         SELECT ?investigator WHERE {{
#             <{project_instance}> <http://www.semanticweb.org/tesis_inv_cualitativa> ?investigator .
#         }}
#         """
#         return self.graph.query(investigators_query)
#
#     def get_investigator_name(self, investigator_instance):
#         """Retorna el atributo 'Nombre' de un investigador."""
#         inv_name_query = f"""
#         SELECT ?nombre WHERE {{
#             <{investigator_instance}> <http://www.semanticweb.org/tesis_inv_cualitativa#Nombre> ?nombre .
#         }}
#         """
#         result = self.graph.query(inv_name_query)
#         for row in result:
#             return str(row.nombre)
#         return None
#
#     def get_objectives_for_project(self, project_instance):
#         """Retorna los objetivos relacionados con un proyecto."""
#         objectives_query = f"""
#         SELECT ?objective WHERE {{
#             <{project_instance}> <http://www.semanticweb.org/tesis_inv_cualitativa#Tiene_objetivo> ?objective .
#         }}
#         """
#         return self.graph.query(objectives_query)
