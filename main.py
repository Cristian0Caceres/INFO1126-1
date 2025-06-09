from RouteTracker import RouteTracker
from vertex import Vertex
from graph import Graph
from edge import Edge
from route_manager import RouteManager

def build_sample_graph():
    """Construcion de grafos"""
    graph = Graph(directed=False)
    
    # Creacion de nodos
    nodes = {
        'Almacen': graph.insert_vertex('Almacen'),
        'Cliente1': graph.insert_vertex('Cliente1'),
        'Cliente2': graph.insert_vertex('Cliente2'),
        'Estacion1': graph.insert_vertex('Estacion1'),
        'Estacion2': graph.insert_vertex('Estacion2'),
        'Punto1': graph.insert_vertex('Punto1'),
        'Punto2': graph.insert_vertex('Punto2'),
        'Punto3': graph.insert_vertex('Punto3'),
    }
    
    # Crear conexiones
    connections = [
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
    
    for u_name, v_name, cost in connections:
        u = nodes[u_name]
        v = nodes[v_name]
        graph.insert_edge(u, v, cost)
    
    return graph, nodes

def main():
    tracker = RouteTracker()  # Crear instancia de RouteTracker

    # Registrar rutas (cada ruta es una lista de nodos)
    tracker.register_route(["A", "B", "C"], cost=10)
    tracker.register_route(["A", "B", "C"], cost=10)
    tracker.register_route(["A", "D", "E"], cost=15)
    tracker.register_route(["D", "E", "F"], cost=20)
    tracker.register_route(["A", "B", "C"], cost=10)
    tracker.register_route(["A", "D", "E"], cost=15)

    # Mostrar las 3 rutas más frecuentes
    print("🔝 Rutas más frecuentes:")
    top_routes = tracker.get_most_frequent_routes(top_n=3)
    for route_str, freq in top_routes:
        print(f"{route_str}: {freq} veces")

    # Crear el hashmap personalizado y mostrar visitas por nodo
    tracker.create_custom_hashmap()
    print("\n📊 Visitas por nodo:")
    for node, visits in tracker.get_node_visits_stats():
        print(f"{node}: {visits} visitas")

    # Test RouteOptimizer
    from RouteOptimizer import RouteOptimizer
    graph, nodes = build_sample_graph()
    optimizer = RouteOptimizer(tracker, graph)

    origin = 'A'
    destination = 'C'
    print(f"\nProbando optimizador de rutas de {origin} a {destination}:")
    suggested_route = optimizer.suggest_optimized_route(origin, destination)
    print("Ruta sugerida:", " -> ".join(suggested_route))

    pattern_analysis = optimizer.analyze_route_patterns()
    print("\nAnálisis de patrones de rutas:")
    for node, count in pattern_analysis.items():
        print(f"{node}: {count} visitas")

    report = optimizer.get_optimization_report()
    print("\nReporte de optimización:")
    print(report)

    print("=== Enrutador de drones con recarga ===")
    
    # Grafos de ejemplos
    # graph, nodes = build_sample_graph()
    
    # Administrador de rutas
    route_manager = RouteManager(graph)
    
    # Guardar estacion de recarga
    route_manager.add_recharge_station('Estacion1')
    route_manager.add_recharge_station('Estacion2')
    
    # Parametros de pruebas
    origin = 'Almacen'
    destination = 'Cliente2'
    battery_limit = 50
    
    print(f"\nBuscando ruta de {origin} a {destination} con bateria limitada a {battery_limit}...")
    
    try:
        # Buscar una ruta de recarga
        result = route_manager.find_route_with_recharge(origin, destination, battery_limit)
        
        # Mostrar resultados
        print("\nRuta encontrada:")
        print(" -> ".join(result['path']))
        print(f"\nCosto total: {result['total_cost']}")
        print(f"Estaciones de recarga utilizadas: {', '.join(result['recharge_stops']) if result['recharge_stops'] else 'Ninguna'}")
        
        print("\nSegmentos de viaje:")
        for i, segment in enumerate(result['segments'], 1):
            print(f"Segmento {i}: {' -> '.join(segment)}")
    
    except ValueError as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()

"""
Resultados esperados al ejecutar el programa:

🔝 Rutas más frecuentes:
A→B→C: 3 veces
A→D→E: 2 veces
D→E→F: 1 veces

📊 Visitas por nodo:
A: 5 visitas
B: 3 visitas
C: 3 visitas
D: 3 visitas
E: 3 visitas
F: 1 visitas

Explicación:
- La ruta "A→B→C" se registró 3 veces.
- La ruta "A→D→E" se registró 2 veces.
- La ruta "D→E→F" se registró 1 vez.

Visitas a nodos:
- Nodo A: aparece en 5 rutas en total (3 veces en A-B-C y 2 veces en A-D-E)
- Nodo B: aparece 3 veces (solo en A-B-C)
- Nodo C: aparece 3 veces (solo en A-B-C)
- Nodo D: aparece 3 veces (2 veces en A-D-E y 1 vez en D-E-F)
- Nodo E: aparece 3 veces (2 veces en A-D-E y 1 vez en D-E-F)
- Nodo F: aparece 1 vez (solo en D-E-F)
"""