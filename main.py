import heapq
import random
from collections import deque, defaultdict
from datetime import datetime
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --------------------------
#   Estructuras Basicas
# --------------------------

class Vertex:
    """Lightweight vertex structure for a graph."""
    __slots__ = '_element'

    def __init__(self, element):
        """Do not call constructor directly. Use Graph's insert_vertex(element)."""
        self._element = element

    def element(self):
        """Return element associated with this vertex."""
        return self._element

    def __hash__(self):
        return hash(id(self))

    def __str__(self):
        return str(self._element)

    def __repr__(self):
        return f"Vertex({self._element})"


class Edge:
    """Lightweight edge structure for a graph."""
    __slots__ = '_origin', '_destination', '_element'

    def __init__(self, u, v, x):
        """Do not call constructor directly. Use Graph's insert_edge(u,v,x)."""
        self._origin = u
        self._destination = v
        self._element = x

    def endpoints(self):
        """Return (u,v) tuple for vertices u and v."""
        return (self._origin, self._destination)

    def opposite(self, v):
        """Return the vertex that is opposite v on this edge."""
        return self._destination if v is self._origin else self._origin

    def element(self):
        """Return element associated with this edge."""
        return self._element

    def __hash__(self):
        """Allow edge to be a map/set key."""
        return hash((self._origin, self._destination))

    def __str__(self):
        """String representation of the edge."""
        return f"({self._origin}->{self._destination}):{self._element}"

    def __repr__(self):
        """Official string representation."""
        return f"Edge({self._origin}, {self._destination}, {self._element})"


class Graph:
    """Representation of a simple graph using an adjacency map."""
    def __init__(self, directed=False):
        """Create an empty graph (undirected, by default)."""
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def is_directed(self):
        """Return True if this is a directed graph; False if undirected."""
        return self._directed

    def insert_vertex(self, element):
        """Insert and return a new Vertex with element."""
        v = Vertex(element)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, element):
        """Insert and return a new Edge from u to v with element."""
        e = Edge(u, v, element)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
        return e

    def remove_edge(self, u, v):
        """Remove the edge between u and v."""
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        """Remove vertex v and all its incident edges."""
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        """Return the edge between u and v, or None if not adjacent."""
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        """Return an iteration of all vertices in the graph."""
        return self._outgoing.keys()

    def edges(self):
        """Return a set of all edges in the graph."""
        seen = set()
        for map in self._outgoing.values():
            seen.update(map.values())
        return seen

    def neighbors(self, v):
        """Return an iteration over all neighbors of vertex v."""
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        """Return number of (outgoing) edges incident to vertex v."""
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        """Return all (outgoing) edges incident to vertex v."""
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()


# --------------------------
#  Componentes del Sistema
# --------------------------

class RouteManager:
    """Gestiona rutas considerando estaciones de recarga."""
    def __init__(self, graph):
        self.graph = graph
        self.recharge_stations = set()

    def add_recharge_station(self, vertex_id):
        """Registra una estacion de recarga."""
        self.recharge_stations.add(vertex_id)

    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        """
        Encuentra la ruta optima considerando limitaciones de bateria.
        
        Returns:
            dict: Contiene 'path', 'total_cost', 'recharge_stops', 'segments'
        """
        # Verificar y obtener vertices
        origin = None
        destination = None
        vertices_map = {}
        
        for v in self.graph.vertices():
            vertices_map[str(v.element())] = v
            if str(v.element()) == str(origin_id):
                origin = v
            if str(v.element()) == str(destination_id):
                destination = v
                
        if not origin or not destination:
            raise ValueError("Vertice no encontrado, error con el origen y destino")
            
        # Caso especial: origen y destino iguales
        if origin == destination:
            return {
                'path': [origin_id],
                'total_cost': 0,
                'recharge_stops': [],
                'segments': [[origin_id]]
            }
            
        # BFS modificado para considerar bateria
        queue = deque()
        queue.append((origin, [origin_id], battery_limit, 0, [], []))
        
        visited = {}  # {vertex_id: (remaining_battery, total_cost)}
        best_solution = None
        
        while queue:
            current_vertex, path, remaining_battery, total_cost, recharge_stops, segments = queue.popleft()
            current_id = str(current_vertex.element())
            
            # Si llegamos al destino, guardar solucion si es mejor
            if current_vertex == destination:
                completed_segments = segments.copy()
                if not completed_segments:
                    completed_segments.append([origin_id, destination_id])
                else:
                    completed_segments[-1].append(destination_id)
                    
                if best_solution is None or total_cost < best_solution['total_cost']:
                    best_solution = {
                        'path': path,
                        'total_cost': total_cost,
                        'recharge_stops': recharge_stops,
                        'segments': completed_segments
                    }
                continue
                
            # Verificar si ya visitamos este nodo con mejor o igual bateria y costo
            if current_id in visited:
                stored_battery, stored_cost = visited[current_id]
                if stored_battery >= remaining_battery and stored_cost <= total_cost:
                    continue
            visited[current_id] = (remaining_battery, total_cost)
            
            # Explorar vecinos
            for neighbor in self.graph.neighbors(current_vertex):
                neighbor_id = str(neighbor.element())
                edge = self.graph.get_edge(current_vertex, neighbor)
                edge_cost = edge.element() if edge else 0
                
                is_recharge_station = neighbor_id in self.recharge_stations
                
                # Opcion 1: Ir al vecino sin recargar
                if edge_cost <= remaining_battery:
                    new_remaining = remaining_battery - edge_cost
                    new_path = path + [neighbor_id]
                    new_total_cost = total_cost + edge_cost
                    new_recharge_stops = recharge_stops.copy()
                    new_segments = segments.copy()
                    
                    if not new_segments:
                        new_segments.append([origin_id, neighbor_id])
                    else:
                        if current_id not in new_segments[-1]:
                            new_segments.append([current_id, neighbor_id])
                        else:
                            new_segments[-1].append(neighbor_id)
                    
                    queue.append((neighbor, new_path, new_remaining, new_total_cost, 
                                new_recharge_stops, new_segments))
                
                # Opcion 2: Considerar recarga si es necesario o estamos en estacion
                if edge_cost > remaining_battery or is_recharge_station:
                    if current_id in self.recharge_stations and current_id not in recharge_stops:
                        new_remaining = battery_limit
                        new_path = path.copy()
                        new_total_cost = total_cost
                        new_recharge_stops = recharge_stops + [current_id]
                        new_segments = segments.copy()
                        
                        queue.append((current_vertex, new_path, new_remaining, new_total_cost, 
                                    new_recharge_stops, new_segments))
                    else:
                        # Buscar estacion de recarga mas cercana
                        nearest_station = self._find_nearest_recharge_station(current_vertex, battery_limit)
                        if nearest_station:
                            station_id = str(nearest_station.element())
                            new_path = path + [station_id]
                            new_recharge_stops = recharge_stops + [station_id]
                            new_remaining = battery_limit
                            new_total_cost = total_cost + edge_cost
                            new_segments = segments.copy()
                            new_segments.append([current_id, station_id])
                            
                            queue.append((nearest_station, new_path, new_remaining, new_total_cost, 
                                        new_recharge_stops, new_segments))
        
        if best_solution is None:
            raise ValueError("No se encontro una ruta valida entre los vertices")
            
        return best_solution
        
    def _find_nearest_recharge_station(self, from_vertex, battery_limit):
        """Encuentra la estacion de recarga mas cercana alcanzable con la bateria actual."""
        queue = deque()
        queue.append((from_vertex, 0))
        visited = set()
        
        while queue:
            current_vertex, current_cost = queue.popleft()
            current_id = str(current_vertex.element())
            
            if current_id in self.recharge_stations:
                return current_vertex
                
            if current_id in visited:
                continue
            visited.add(current_id)
            
            for neighbor in self.graph.neighbors(current_vertex):
                edge = self.graph.get_edge(current_vertex, neighbor)
                edge_cost = edge.element() if edge else 0
                total_cost = current_cost + edge_cost
                
                if total_cost <= battery_limit:
                    queue.append((neighbor, total_cost))
                    
        return None


class AVLNode:
    """Nodo para el arbol AVL."""
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0  # nodo singular tiene altura 0


def avl_height(N):
    return -1 if N is None else N.height


def avl_get_balance(N):
    return 0 if N is None else avl_height(N.left) - avl_height(N.right)


def avl_right_rotate(y):
    x = y.left
    T2 = x.right

    # Rotacion
    x.right = y
    y.left = T2

    # Actualizar alturas
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1

    return x


def avl_left_rotate(x):
    y = x.right
    T2 = y.left

    # Rotacion
    y.left = x
    x.right = T2

    # Actualizar alturas
    x.height = max(avl_height(x.left), avl_height(x.right)) + 1
    y.height = max(avl_height(y.left), avl_height(y.right)) + 1

    return y


def avl_insert(node, key):
    if node is None:
        return AVLNode(key)

    if key < node.key:
        node.left = avl_insert(node.left, key)
    elif key > node.key:
        node.right = avl_insert(node.right, key)
    else:
        return node  # no se permiten duplicados

    node.height = max(avl_height(node.left), avl_height(node.right)) + 1
    balance = avl_get_balance(node)

    # Casos de desbalanceo
    if balance > 1 and key < node.left.key:
        return avl_right_rotate(node)
    if balance < -1 and key > node.right.key:
        return avl_left_rotate(node)
    if balance > 1 and key > node.left.key:
        node.left = avl_left_rotate(node.left)
        return avl_right_rotate(node)
    if balance < -1 and key < node.right.key:
        node.right = avl_right_rotate(node.right)
        return avl_left_rotate(node)

    return node


def avl_min_value_node(node):
    current = node
    while current.left:
        current = current.left
    return current


def avl_delete_node(root, key):
    if root is None:
        return root

    if key < root.key:
        root.left = avl_delete_node(root.left, key)
    elif key > root.key:
        root.right = avl_delete_node(root.right, key)
    else:
        if root.left is None or root.right is None:
            root = root.left or root.right
        else:
            temp = avl_min_value_node(root.right)
            root.key = temp.key
            root.right = avl_delete_node(root.right, temp.key)

    if root is None:
        return root

    root.height = max(avl_height(root.left), avl_height(root.right)) + 1
    balance = avl_get_balance(root)

    if balance > 1 and avl_get_balance(root.left) >= 0:
        return avl_right_rotate(root)
    if balance > 1 and avl_get_balance(root.left) < 0:
        root.left = avl_left_rotate(root.left)
        return avl_right_rotate(root)
    if balance < -1 and avl_get_balance(root.right) <= 0:
        return avl_left_rotate(root)
    if balance < -1 and avl_get_balance(root.right) > 0:
        root.right = avl_right_rotate(root.right)
        return avl_left_rotate(root)

    return root


def avl_in_order(node):
    """Recorrido inorden del arbol AVL."""
    if node is None:
        return []
    return avl_in_order(node.left) + [node.key] + avl_in_order(node.right)


class HashMap:
    """Implementacion basica de un HashMap con encadenamiento."""
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        """Funcion hash simple basada en suma de codigos ASCII."""
        return sum(ord(c) for c in str(key)) % self.size

    def put(self, key, value):
        """Inserta o actualiza un par clave-valor."""
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                pair[1] = value
                return
        self.table[index].append([key, value])

    def get(self, key):
        """Obtiene el valor asociado a una clave."""
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                return pair[1]
        return None

    def items(self):
        """Genera todos los pares clave-valor."""
        for bucket in self.table:
            for key, value in bucket:
                yield key, value


class RouteTracker:
    """Registra y analiza rutas historicas."""
    def __init__(self):
        self.root = None
        self.route_counts = {}
        self.node_visits = {}
        self.custom_hashmap = None
        self.total_routes = 0

    def _route_to_str(self, route):
        """Convierte ruta a string con formato 'A→B→C'."""
        if not route or not isinstance(route, list):
            raise ValueError("La ruta debe ser una lista no vacia de nodos")
        return "→".join(str(node) for node in route)

    def register_route(self, route_path, cost=None):
        """Registra una ruta y actualiza estadisticas."""
        route_str = self._route_to_str(route_path)
        
        # Actualizar AVL y conteo de rutas
        self.root = avl_insert(self.root, route_str)
        self.route_counts[route_str] = self.route_counts.get(route_str, 0) + 1
        self.total_routes += 1
        
        # Actualizar visitas a nodos
        for node in route_path:
            node_str = str(node)
            self.node_visits[node_str] = self.node_visits.get(node_str, 0) + 1

    def get_most_frequent_routes(self, top_n=5):
        """Obtiene las rutas mas frecuentes ordenadas por frecuencia."""
        all_routes = avl_in_order(self.root)
        freq_list = [(route, self.route_counts[route]) for route in all_routes if route in self.route_counts]
        freq_list.sort(key=lambda x: (-x[1], x[0]))  # Ordenar por frecuencia (desc) y luego alfabeticamente
        return freq_list[:top_n]

    def get_node_visits_stats(self, sorted_by='visits'):
        """Obtiene estadisticas de nodos visitados."""
        if not self.custom_hashmap:
            self.create_custom_hashmap()
            
        items = list(self.custom_hashmap.items())
        if sorted_by == 'visits':
            items.sort(key=lambda x: (-x[1], x[0]))  # Ordenar por visitas (desc)
        elif sorted_by == 'node':
            items.sort(key=lambda x: x[0])  # Ordenar alfabeticamente por nodo
            
        return items

    def create_custom_hashmap(self, initial_size=10):
        """Crea un HashMap personalizado con las visitas a nodos."""
        self.custom_hashmap = HashMap(size=initial_size)
        for node, visits in self.node_visits.items():
            self.custom_hashmap.put(node, visits)

    def generate_report(self):
        """Genera un reporte estadistico completo."""
        report = []
        report.append(f"Total de rutas registradas: {self.total_routes}")
        
        top_routes = self.get_most_frequent_routes(5)
        report.append("\nTop 5 rutas mas frecuentes:")
        for i, (route, count) in enumerate(top_routes, 1):
            report.append(f"{i}. {route}: {count} veces ({count/self.total_routes:.1%})")
            
        node_stats = self.get_node_visits_stats('visits')
        report.append("\nTop 5 nodos mas visitados:")
        for i, (node, visits) in enumerate(node_stats[:5], 1):
            report.append(f"{i}. {node}: {visits} visitas")
            
        return "\n".join(report)


class RouteOptimizer:
    """Optimiza rutas basandose en datos historicos."""
    def __init__(self, route_tracker, graph):
        self.route_tracker = route_tracker
        self.graph = graph
        self.optimization_report = []
        self.node_scores = self._calculate_node_scores()

    def _calculate_node_scores(self):
        """Calcula puntuacion para cada nodo basada en frecuencia de visita."""
        node_scores = defaultdict(int)
        total_visits = sum(self.route_tracker.node_visits.values())
        
        for node, visits in self.route_tracker.node_visits.items():
            node_scores[node] = visits / total_visits * 100
            
        return node_scores

    def suggest_optimized_route(self, origin, destination, battery_limit=None):
        """Sugiere ruta optima considerando multiples factores."""
        origin_str, dest_str = str(origin), str(destination)
        self.optimization_report = [f"Optimizando ruta de {origin_str} a {dest_str}"]
        
        # 1. Buscar ruta exacta frecuente
        exact_routes = self._find_exact_routes(origin_str, dest_str)
        if exact_routes:
            return exact_routes[0].split("→")
            
        # 2. Buscar combinacion de segmentos
        combined_route = self._combine_route_segments(origin_str, dest_str)
        if combined_route:
            return combined_route
            
        # 3. Calcular nueva ruta con Dijkstra
        return self._calculate_new_route(origin_str, dest_str, battery_limit)

    def _find_exact_routes(self, origin, destination):
        """Busca rutas exactas en el historial."""
        routes = [route for route, _ in self.route_tracker.get_most_frequent_routes(50) 
                if route.startswith(origin) and route.endswith(destination)]
        
        if routes:
            self.optimization_report.append(f"Usando ruta exacta frecuente: {routes[0]}")
        return routes

    def _combine_route_segments(self, origin, destination):
        """Intenta combinar segmentos de rutas conocidas."""
        common_nodes = set()
        
        # Buscar nodos que aparecen en rutas con origen y destino
        for route, _ in self.route_tracker.get_most_frequent_routes(100):
            nodes = route.split("→")
            if origin in nodes and destination in nodes:
                common_nodes.update(nodes)
                
        if not common_nodes:
            return None
            
        # Buscar el nodo intermedio con mejor puntuacion
        best_node = max(common_nodes, key=lambda x: self.node_scores.get(x, 0))
        
        # Construir ruta combinada
        combined_route = f"{origin}→{best_node}→{destination}"
        self.optimization_report.append(f"Combinando segmentos usando nodo intermedio {best_node}")
        return combined_route.split("→")

    def _calculate_new_route(self, origin, destination, battery_limit):
        """Calcula nueva ruta usando Dijkstra considerando bateria."""
        self.optimization_report.append("Calculando nueva ruta con algoritmo de busqueda")
        
        # Implementacion simplificada - en realidad deberia usar el grafo
        # Esto es un placeholder - la implementacin real usaria el grafo
        return [origin, destination]

    def analyze_route_patterns(self):
        """Analiza patrones en las rutas mas frecuentes."""
        node_visit_counts = defaultdict(int)
        for route, freq in self.route_tracker.get_most_frequent_routes(50):
            nodes = route.split("→")
            for node in nodes:
                node_visit_counts[node] += freq
                
        self.optimization_report.append(f"Analisis de patrones: nodos visitados con frecuencia {dict(node_visit_counts)}")
        return node_visit_counts

    def get_optimization_report(self):
        """Devuelve reporte de optimizaciones aplicadas."""
        return "\n".join(self.optimization_report)


class OrderSimulator:
    """Simula ordenes de entrega con drones."""
    def __init__(self):
        self.graph = Graph(directed=False)
        self.max_energy = 20  # Energia maxima del dron
        self.stats = {
            'total_orders': 0,
            'delivered': 0,
            'failed': 0,
            'total_cost': 0,
            'total_recharges': 0
        }

        # Crear vertices y aristas
        self.vertices = {}
        self._initialize_graph()

    def _initialize_graph(self):
        """Inicializa el grafo con nodos y conexiones."""
        # Nodos
        nodes = [
            ('A', 'almacen'),
            ('B', 'intermedio'),
            ('C', 'intermedio'),
            ('R1', 'recarga'),
            ('R2', 'recarga'),
            ('X', 'cliente'),
            ('Y', 'cliente'),
            ('Z', 'cliente')
        ]
        for nombre, tipo in nodes:
            v = self.graph.insert_vertex(nombre)
            self.vertices[nombre] = {'vertice': v, 'tipo': tipo}

        # Conexiones
        conexiones = [
            ('A', 'R1', 5),
            ('R1', 'B', 5),
            ('A', 'B', 12),
            ('R1', 'R2', 6),
            ('R2', 'C', 4),
            ('B', 'C', 10),
            ('C', 'X', 15),
            ('C', 'Y', 20),
            ('C', 'Z', 25)
        ]
        for origen, destino, costo in conexiones:
            u = self.vertices[origen]['vertice']
            v = self.vertices[destino]['vertice']
            self.graph.insert_edge(u, v, costo)

        # Diccionarios para seleccion aleatoria
        self.almacenes = {'Almacen_A': 'A'}
        self.clientes = {
            'Cliente_X': 'X',
            'Cliente_Y': 'Y',
            'Cliente_Z': 'Z'
        }

    def dijkstra(self, origin_id):
        """Implementacion del algoritmo de Dijkstra para caminos mas cortos."""
        origen_v = self.vertices[origin_id]['vertice']
        dist = {v: float('inf') for v in self.graph.vertices()}
        prev = {v: None for v in self.graph.vertices()}
        dist[origen_v] = 0

        pq = [(0, origen_v)]  # cola de prioridad

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: 
                continue
            for edge in self.graph.incident_edges(u):
                v = edge.opposite(u)
                peso = edge.element()
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        return dist, prev

    def reconstruir_camino(self, prev, destino_v):
        """Reconstruye el camino desde el destino hasta el origen."""
        camino = []
        actual = destino_v
        while actual:
            camino.append(actual)
            actual = prev[actual]
        camino.reverse()
        return camino

    def calcular_paradas(self, ruta_ids):
        """Calcula las paradas de recarga necesarias para una ruta."""
        energia = self.max_energy
        paradas = []
        total = 0

        for i in range(len(ruta_ids) - 1):
            actual = ruta_ids[i]
            siguiente = ruta_ids[i + 1]
            u = self.vertices[actual]['vertice']
            v = self.vertices[siguiente]['vertice']
            edge = self.graph.get_edge(u, v)
            consumo = edge.element()
            total += consumo
            energia -= consumo

            if energia <= 0:
                tipo = self.vertices[actual]['tipo']
                if tipo == 'recarga':
                    paradas.append(actual)
                    energia = self.max_energy
                else:
                    paradas.append(f"Advertencia: energia insuficiente en {actual} forzando parada")
                    energia = self.max_energy

        return paradas, total

    def process_orders(self, cantidad=5):
        """Procesa multiples ordenes de entrega."""
        print(f"\n=== Simulando {cantidad} ordenes ===")
        print(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for i in range(1, cantidad + 1):
            result = self._process_single_order(i)
            self._print_order_result(result)
            self._update_stats(result)
            
        self._print_final_stats()

    def _process_single_order(self, order_num):
        """Procesa una sola orden de entrega."""
        origen_nom = random.choice(list(self.almacenes.keys()))
        destino_nom = random.choice(list(self.clientes.keys()))
        origen_id = self.almacenes[origen_nom]
        destino_id = self.clientes[destino_nom]

        dist, prev = self.dijkstra(origen_id)
        destino_v = self.vertices[destino_id]['vertice']
        camino_vertices = self.reconstruir_camino(prev, destino_v)
        camino_ids = [v.element() for v in camino_vertices]

        recargas, costo_real = self.calcular_paradas(camino_ids)
        
        return {
            'orden': order_num,
            'origen': origen_nom,
            'destino': destino_nom,
            'ruta': camino_ids,
            'costo': costo_real,
            'recargas': recargas,
            'estado': 'Entregado' if not any("Advertencia" in r for r in recargas) else 'Fallido'
        }

    def _print_order_result(self, result):
        """Imprime el resultado de una orden con formato estandar."""
        print(f"Orden #{result['orden']}: {result['origen']} → {result['destino']}")
        print(f"Ruta: {' → '.join(result['ruta'])}")
        print(f"Costo: {result['costo']} | Paradas de recarga: {result['recargas']}")
        print(f"Estado: {result['estado']}\n")

    def _update_stats(self, result):
        """Actualiza las estadisticas globales."""
        self.stats['total_orders'] += 1
        if result['estado'] == 'Entregado':
            self.stats['delivered'] += 1
        else:
            self.stats['failed'] += 1
            
        self.stats['total_cost'] += result['costo']
        self.stats['total_recharges'] += len(result['recargas'])

    def _print_final_stats(self):
        """Imprime estadisticas finales del simulador."""
        print("\n=== Estadisticas Finales ===")
        print(f"Total ordenes procesadas: {self.stats['total_orders']}")
        success_rate = self.stats['delivered'] / self.stats['total_orders'] if self.stats['total_orders'] > 0 else 0
        print(f"Entregas exitosas: {self.stats['delivered']} ({success_rate:.1%})")
        print(f"Entregas fallidas: {self.stats['failed']}")
        print(f"Costo total acumulado: {self.stats['total_cost']}")
        print(f"Paradas de recarga totales: {self.stats['total_recharges']}")
        print(f"\nHora de finalizacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# --------------------------
#     Funcion Principal
# --------------------------

def main():
    """Funcion principal que demuestra el sistema completo."""
    # 1. Demostracion de RouteTracker
    print("=== DEMOSTRACION DEL SISTEMA DE GESTION DE RUTAS PARA DRONES ===")
    print("\n1. Probando RouteTracker (Registro y Analisis de Rutas)")
    
    tracker = RouteTracker()
    
    # Registrar algunas rutas de ejemplo
    rutas_ejemplo = [
        ["A", "B", "C"],
        ["A", "B", "C"],
        ["A", "D", "E"],
        ["D", "E", "F"],
        ["A", "B", "C"],
        ["A", "D", "E"]
    ]
    
    for ruta in rutas_ejemplo:
        tracker.register_route(ruta)
    
    # Mostrar estadisticas
    print("\nEstadisticas de rutas:")
    print(tracker.generate_report())
    
    # 2. Demostracion de RouteOptimizer
    print("\n2. Probando RouteOptimizer (Optimizacion de Rutas)")
    
    # Crear un grafo de ejemplo
    graph = Graph(directed=False)
    nodes = {
        'A': graph.insert_vertex('A'),
        'B': graph.insert_vertex('B'),
        'C': graph.insert_vertex('C'),
        'D': graph.insert_vertex('D'),
        'E': graph.insert_vertex('E'),
        'F': graph.insert_vertex('F')
    }
    
    # Añadir algunas conexiones
    graph.insert_edge(nodes['A'], nodes['B'], 10)
    graph.insert_edge(nodes['B'], nodes['C'], 15)
    graph.insert_edge(nodes['A'], nodes['D'], 20)
    graph.insert_edge(nodes['D'], nodes['E'], 10)
    graph.insert_edge(nodes['E'], nodes['F'], 5)
    graph.insert_edge(nodes['B'], nodes['E'], 30)
    
    optimizer = RouteOptimizer(tracker, graph)
    
    # Optimizar una ruta
    ruta_optimizada = optimizer.suggest_optimized_route('A', 'C')
    print(f"\nRuta optimizada sugerida: {' → '.join(ruta_optimizada)}")
    
    # Mostrar reporte de optimizacion
    print("\nReporte de optimizacion:")
    print(optimizer.get_optimization_report())
    
    # 3. Demostracion de OrderSimulator
    print("\n3. Probando OrderSimulator (Simulacion de Entregas)")
    simulator = OrderSimulator()
    simulator.process_orders(3)
    
    # 4. Demostracion de RouteManager con recargas
    print("\n4. Probando RouteManager con Gestion de Recarga")
    
    # Crear grafo con estaciones de recarga
    graph_recarga = Graph(directed=False)
    nodes_recarga = {
        'Almacen': graph_recarga.insert_vertex('Almacen'),
        'Cliente1': graph_recarga.insert_vertex('Cliente1'),
        'Cliente2': graph_recarga.insert_vertex('Cliente2'),
        'Estacion1': graph_recarga.insert_vertex('Estacion1'),
        'Estacion2': graph_recarga.insert_vertex('Estacion2'),
        'Punto1': graph_recarga.insert_vertex('Punto1'),
        'Punto2': graph_recarga.insert_vertex('Punto2'),
        'Punto3': graph_recarga.insert_vertex('Punto3'),
    }
    
    # Crear conexiones
    conexiones = [
        ('Almacen', 'Punto1', 20),
        ('Punto1', 'Estacion1', 15),
        ('Estacion1', 'Cliente1', 30),
        ('Almacen', 'Punto2', 35),
        ('Punto2', 'Estacion2', 10),
        ('Estacion2', 'Cliente2', 25),
        ('Punto1', 'Punto3', 40),
        ('Punto3', 'Estacion2', 20),
        ('Punto2', 'Punto3', 15),
    ]
    
    for u_name, v_name, cost in conexiones:
        u = nodes_recarga[u_name]
        v = nodes_recarga[v_name]
        graph_recarga.insert_edge(u, v, cost)
    
    # Configurar RouteManager
    route_manager = RouteManager(graph_recarga)
    route_manager.add_recharge_station('Estacion1')
    route_manager.add_recharge_station('Estacion2')
    
    # Buscar ruta con limitacion de bateria
    print("\nBuscando ruta de Almacen a Cliente2 con bateria limitada a 50...")
    try:
        result = route_manager.find_route_with_recharge('Almacen', 'Cliente2', 50)
        
        print("\nRuta encontrada:")
        print(" → ".join(result['path']))
        print(f"\nCosto total: {result['total_cost']}")
        print(f"Estaciones de recarga utilizadas: {', '.join(result['recharge_stops']) if result['recharge_stops'] else 'Ninguna'}")
        
        print("\nSegmentos de viaje:")
        for i, segment in enumerate(result['segments'], 1):
            print(f"Segmento {i}: {' → '.join(segment)}")
    
    except ValueError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()