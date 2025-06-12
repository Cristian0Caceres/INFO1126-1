from vertex import Vertex
from graph import Graph
from edge import Edge
from route_manager import RouteManager

def recibir_datos_simulacion_nx(G_nx, n_orders):
    """Recibe un grafo NetworkX y realiza simulación de rutas."""
    print("=== Enrutador de drones con recarga ===")

    graph = Graph(directed=False)
    node_map = {}

    for node in G_nx.nodes:
        v = graph.insert_vertex(str(node))
        node_map[node] = v

    for u, v, data in G_nx.edges(data=True):
        weight = data.get("weight", 1)  # Peso por defecto
        graph.insert_edge(node_map[u], node_map[v], weight)

    route_manager = RouteManager(graph)

    # Agregar estaciones de recarga
    for node, data in G_nx.nodes(data=True):
        if data.get("role") == "🔋 Recarga":
            route_manager.add_recharge_station(str(node))

    # Buscar un almacén y un cliente
    almacen = next((str(n) for n, d in G_nx.nodes(data=True) if d["role"] == "📦 Almacenamiento"), None)
    cliente = next((str(n) for n, d in G_nx.nodes(data=True) if d["role"] == "👤 Cliente"), None)

    if not almacen or not cliente:
        print("Error: No se encontró almacén o cliente en el grafo.")
        return

    battery_limit = 50  # Puedes hacerlo configurable si lo deseas

    print(f"\nRuta de {almacen} a {cliente} con batería {battery_limit}...")

    try:
        result = route_manager.find_route_with_recharge(almacen, cliente, battery_limit)

        print("\nRuta encontrada:")
        print(" -> ".join(result['path']))
        print(f"\nCosto total: {result['total_cost']}")
        print(f"Estaciones de recarga: {', '.join(result['recharge_stops']) if result['recharge_stops'] else 'Ninguna'}")

        print("\nSegmentos de viaje:")
        for i, segment in enumerate(result['segments'], 1):
            print(f"Segmento {i}: {' -> '.join(segment)}")

    except ValueError as e:
        print(f"\nError: {e}")
