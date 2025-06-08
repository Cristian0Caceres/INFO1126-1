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
    print("=== Enrutador de drones con recarga ===")
    
    # Grafos de ejemplos
    graph, nodes = build_sample_graph()
    
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