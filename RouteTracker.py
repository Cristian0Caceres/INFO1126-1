import AVL  # Se importa el módulo AVL que implementa el árbol AVL (equilibrado)
from Hashmap import HashMap  # Se importa un HashMap personalizado

class RouteTracker:
    def __init__(self):
        self.root = None                 # Raíz del árbol AVL que almacenará las rutas ordenadas
        self.route_counts = {}           # Diccionario para contar la frecuencia de cada ruta (clave: ruta en string, valor: conteo)
        self.node_visits = {}            # Diccionario para contar la cantidad de visitas por cada nodo individual
        self.custom_hashmap = None       # Variable para almacenar un hashmap personalizado, se inicializa después

    def _route_to_str(self, route):
        # Convierte una lista de nodos de una ruta en una cadena separada por "→" para usar como clave
        return "→".join(route)

    def register_route(self, route_path, cost=None):
        """Registra una ruta en el sistema y actualiza las estadísticas de frecuencia y visitas por nodo."""
        route_str = self._route_to_str(route_path)  # Convierte la ruta a string para usarla en el AVL y conteos

        if route_str not in self.route_counts:
            # Si la ruta es nueva, se inserta en el AVL y se inicia el conteo en 1
            self.root = AVL.insert(self.root, route_str)
            self.route_counts[route_str] = 1
        else:
            # Si ya existe, solo se incrementa el conteo
            self.route_counts[route_str] += 1

        # Actualiza el conteo de visitas para cada nodo que aparece en la ruta
        for node in route_path:
            self.node_visits[node] = self.node_visits.get(node, 0) + 1

    def get_most_frequent_routes(self, top_n=5):
        """Devuelve una lista con las top N rutas más frecuentes, ordenadas por frecuencia descendente."""
        all_routes = self._in_order(self.root)  # Obtiene todas las rutas ordenadas del AVL
        # Construye una lista de tuplas (ruta, frecuencia) usando el diccionario route_counts
        freq_list = [(route, self.route_counts.get(route, 0)) for route in all_routes]
        freq_list.sort(key=lambda x: x[1], reverse=True)  # Ordena por frecuencia de mayor a menor
        return freq_list[:top_n]  # Devuelve solo las top N rutas

    def _in_order(self, node):
        """Recorrido inorden del árbol AVL para obtener una lista ordenada de rutas."""
        if node is None:
            return []
        # Recorre el subárbol izquierdo, el nodo actual y el subárbol derecho (orden ascendente)
        return self._in_order(node.left) + [node.key] + self._in_order(node.right)

    def get_node_visits_stats(self):
        """Obtiene las estadísticas de visitas a nodos usando el hashmap personalizado."""
        if not self.custom_hashmap:
            # Si el hashmap no fue inicializado, lanza un error para avisar al usuario
            raise Exception("HashMap no inicializado. Llama a create_custom_hashmap() primero.")
        return list(self.custom_hashmap.items())  # Devuelve la lista de pares (nodo, visitas) del hashmap

    def create_custom_hashmap(self, initial_size=10):
        """Crea un hashmap personalizado e inserta en él las visitas por nodo."""
        self.custom_hashmap = HashMap(size=initial_size)  # Inicializa el hashmap con tamaño dado
        for node, visits in self.node_visits.items():
            self.custom_hashmap.put(node, visits)  # Inserta cada nodo con su conteo de visitas en el hashmap
