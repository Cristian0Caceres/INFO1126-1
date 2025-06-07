from RouteTracker import RouteTracker

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
