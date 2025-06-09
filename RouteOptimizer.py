class RouteOptimizer:
    def __init__(self, route_tracker, graph):
        self.route_tracker = route_tracker
        self.graph = graph
        self.optimization_report = []

    def suggest_optimized_route(self, origin_id, destination_id):
        """
        Sugiere ruta basada en patrones historicos

        Prioridad:
        1. si existe ruta exacta frecuente: usar esa
        2. si existen rutas parciales: combinar segmentos conocidos
        3. calcular nueva ruta y registrarla
        """
        # 1. Buscar ruta exacta frecuente
        exact_routes = [route for route, freq in self.route_tracker.get_most_frequent_routes(top_n=10) if route.startswith(origin_id) and route.endswith(destination_id)]
        if exact_routes:
            self.optimization_report.append(f"Usando ruta exacta frecuente: {exact_routes[0]}")
            return exact_routes[0].split("→")

        # 2. Buscar rutas parciales y combinar segmentos
        # Obtener rutas frecuentes que contienen origen y destino
        partial_routes = [route for route, freq in self.route_tracker.get_most_frequent_routes(top_n=20) if origin_id in route and destination_id in route]
        if partial_routes:
            # Heurística simple: elegir la ruta con mayor frecuencia que contiene ambos nodos
            best_route = partial_routes[0]
            self.optimization_report.append(f"Usando ruta parcial frecuente: {best_route}")
            return best_route.split("→")

        # 3. Calcular nueva ruta (ejemplo: camino más corto)
        # Aquí se puede usar un algoritmo de búsqueda en el grafo (Dijkstra, A*, etc.)
        # Para simplicidad, retornamos una lista vacía y registramos la acción
        self.optimization_report.append("Calculando nueva ruta (no implementado)")
        return []

    def analyze_route_patterns(self):
        """
        Analiza patrones en las rutas más frecuentes
        """
        # Ejemplo: contar frecuencia de nodos en rutas frecuentes
        node_visit_counts = {}
        for route, freq in self.route_tracker.get_most_frequent_routes(top_n=50):
            nodes = route.split("→")
            for node in nodes:
                node_visit_counts[node] = node_visit_counts.get(node, 0) + freq
        self.optimization_report.append(f"Análisis de patrones: nodos visitados con frecuencia {node_visit_counts}")
        return node_visit_counts

    def get_optimization_report(self):
        """
        Devuelve reporte de optimizaciones aplicadas
        """
        return "\n".join(self.optimization_report)
