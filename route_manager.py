from collections import deque
from graph import Graph, Vertex
from edge import Edge

class RouteManager:
    def __init__(self, graph):

        #Inicializar RouteManager con un grafo
        self.graph = graph
        self.recharge_stations = set()  # almacenador de las estaciones de recarga
        
    def add_recharge_station(self, vertex_id):
        
        #ID de los vertice de las estaciones de recarga
        self.recharge_stations.add(vertex_id)
        
    def find_route_with_recharge(self, origin_id, destination_id, battery_limit=50):
        
        # Encontrar la ruta optima y genera error si la ruta entre origen y destino no son optimas 
        # verifica si los vertices existen en el grafo
        origin = None
        destination = None
        vertices_map = {}  # mapeo de id de vertices a objetos vertex
        
        
        for v in self.graph.vertices():
            vertices_map[str(v.element())] = v
            if str(v.element()) == str(origin_id):
                origin = v
            if str(v.element()) == str(destination_id):
                destination = v
                
        if not origin or not destination:
            raise ValueError("Vertice no encontrado, error con el origen y destino")
            
        # en caso de que el origen sea el destino
        if origin == destination:
            return {
                'path': [origin_id],
                'total_cost': 0,
                'recharge_stops': [],
                'segments': [[origin_id]]
            }
            
        # BFS
        queue = deque()
        
        # Tupla de cada elemento en la cola
        # (current_vertex, path, remaining_battery, total_cost, recharge_stops, segments)
        queue.append((origin, [origin_id], battery_limit, 0, [], []))
        
        visited = {}  # para evitar ciclos: {vertex_id: (remaining_battery, total_cost)}
        
        best_solution = None
        
        
        while queue:
            current_vertex, path, remaining_battery, total_cost, recharge_stops, segments = queue.popleft()
            current_id = str(current_vertex.element())
            
            # si se llega al destino, se guarda la solucion si es mejor que la actual
            if current_vertex == destination:
                if best_solution is None or total_cost < best_solution['total_cost']:
                    # completar los ultimos segmentos
                    completed_segments = segments.copy()
                    if len(completed_segments) == 0:
                        completed_segments.append([origin_id, destination_id])
                    else:
                        completed_segments[-1].append(destination_id)
                        
                    best_solution = {
                        'path': path,
                        'total_cost': total_cost,
                        'recharge_stops': recharge_stops,
                        'segments': completed_segments
                    }
                continue
                
            # Verificar si ya visitamos este nodo con mejor o igual bateria con un costo mas optimo
            if current_id in visited:
                stored_battery, stored_cost = visited[current_id]
                if stored_battery >= remaining_battery and stored_cost <= total_cost:
                    continue
            visited[current_id] = (remaining_battery, total_cost)
            
            # explorar vecinos
            for neighbor in self.graph.neighbors(current_vertex):
                neighbor_id = str(neighbor.element())
                edge = self.graph.get_edge(current_vertex, neighbor)
                edge_cost = edge.element() if edge else 0
                
                # si el vecino es una de las estaciones de recarga, se considera como opcion
                is_recharge_station = neighbor_id in self.recharge_stations
                
                # se puede llegar al vecino sin recargar
                if edge_cost <= remaining_battery:
                    new_remaining = remaining_battery - edge_cost
                    new_path = path + [neighbor_id]
                    new_total_cost = total_cost + edge_cost
                    new_recharge_stops = recharge_stops.copy()
                    new_segments = segments.copy()
                    
                    # si no hay segmentos, crear el primero
                    if len(new_segments) == 0:
                        new_segments.append([origin_id, neighbor_id])
                    else:
                        # si el ultimo segmento no contiene current_id, es porque ya fue recargados
                        if current_id not in new_segments[-1]:
                            new_segments.append([current_id, neighbor_id])
                        else:
                            new_segments[-1].append(neighbor_id)
                    
                    queue.append((neighbor, new_path, new_remaining, new_total_cost, 
                                new_recharge_stops, new_segments))
                
                # si no podemos llegar al vecino sin recargar
                # se busca la estacion de recarga mas cercana
                if edge_cost > remaining_battery or is_recharge_station:
                    # si se encuentra en la estacion de recarga, recargamos
                    if current_id in self.recharge_stations and current_id not in recharge_stops:
                        new_remaining = battery_limit
                        new_path = path.copy()
                        new_total_cost = total_cost
                        new_recharge_stops = recharge_stops + [current_id]
                        new_segments = segments.copy()
                        
                        # si se recarga, en el proximo movimiento, se inicia el nuevo segmento
                        queue.append((current_vertex, new_path, new_remaining, new_total_cost, 
                                    new_recharge_stops, new_segments))
                    else:
                        # Buscar la estacion de recarga mas cercana
                        nearest_station = self._find_nearest_recharge_station(current_vertex, battery_limit)
                        if nearest_station:
                            station_id = str(nearest_station.element())
                            # agregar ruta a la estacion de recarga
                            new_path = path + [station_id]
                            new_recharge_stops = recharge_stops + [station_id]
                            new_remaining = battery_limit
                            # para simplificar, asumimos que se puede llegar con la bateraa restante
                            new_total_cost = total_cost + edge_cost  #aproximacion
                            new_segments = segments.copy()
                            new_segments.append([current_id, station_id])
                            
                            queue.append((nearest_station, new_path, new_remaining, new_total_cost, 
                                        new_recharge_stops, new_segments))
        
        if best_solution is None:
            raise ValueError("No se encontro una ruta correcta entre los vertices")
            
        return best_solution
        
    def _find_nearest_recharge_station(self, from_vertex, battery_limit):
        # Encontrar la estacion mas cercana segun la bateria actual.
        
        #vertex: vertice de la estacion de recarga mas cercana, en el caso que no se encuentre nonne
        
        # BFS para encontrar la estacion mas cercana
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