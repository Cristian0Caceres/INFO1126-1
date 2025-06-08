from graph import Graph
import heapq  #Dijkstra
import random

class OrderSimulator:
    def __init__(self):
        #grafo 
        self.grafo = Graph(directed=False)
        self.max_energia = 20  # Energia maxima que puede tener un dron
        self.estadisticas = []  # Lista para guardar los resultados

        # Diccionario para guardar los vertices
        self.vertices = {}

        #Nodos
        nodos = [
            ('A', 'almacen'),
            ('B', 'intermedio'),
            ('C', 'intermedio'),
            ('R1', 'recarga'),
            ('R2', 'recarga'),
            ('X', 'cliente'),
            ('Y', 'cliente'),
            ('Z', 'cliente')
        ]
        for nombre, tipo in nodos:
            v = self.grafo.insert_vertex(nombre)
            self.vertices[nombre] = {'vertice': v, 'tipo': tipo}

        # Conecciones
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
            self.grafo.insert_edge(u, v, costo)  #costo como "element" de Edge

        
        self.almacenes = {'Almacen_A': 'A'}
        self.clientes = {
            'Cliente_X': 'X',
            'Cliente_Y': 'Y',
            'Cliente_Z': 'Z'
        }

    #Dijkstra
    def dijkstra(self, origen_id):
        origen_v = self.vertices[origen_id]['vertice']
        dist = {v: float('inf') for v in self.grafo.vertices()}
        prev = {v: None for v in self.grafo.vertices()}
        dist[origen_v] = 0

        pq = [(0, origen_v)]  #cola de prioridad

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]: continue
            for edge in self.grafo.incident_edges(u):
                v = edge.opposite(u)
                peso = edge.element()
                if dist[u] + peso < dist[v]:
                    dist[v] = dist[u] + peso
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        return dist, prev

    # Ruta
    def reconstruir_camino(self, prev, destino_v):
        camino = []
        actual = destino_v
        while actual:
            camino.append(actual)
            actual = prev[actual]
        camino.reverse()
        return camino

    #Calculo de recarga
    def calcular_paradas(self, ruta_ids):
        energia = self.max_energia
        paradas = []
        total = 0

        for i in range(len(ruta_ids) - 1):
            actual = ruta_ids[i]
            siguiente = ruta_ids[i + 1]
            u = self.vertices[actual]['vertice']
            v = self.vertices[siguiente]['vertice']
            edge = self.grafo.get_edge(u, v)
            consumo = edge.element()
            total += consumo
            energia -= consumo

            if energia <= 0:
                tipo = self.vertices[actual]['tipo']
                if tipo == 'recarga':
                    paradas.append(actual)
                    energia = self.max_energia
                else:
                    paradas.append(f"Advertencia: energia insuficiente en {actual} forzando parada")
                    energia = self.max_energia

        return paradas, total

    #Orden de entrega
    def process_orders(self, cantidad=5):
        for i in range(1, cantidad + 1):
            origen_nom = random.choice(list(self.almacenes.keys()))
            destino_nom = random.choice(list(self.clientes.keys()))
            origen_id = self.almacenes[origen_nom]
            destino_id = self.clientes[destino_nom]

            dist, prev = self.dijkstra(origen_id)
            destino_v = self.vertices[destino_id]['vertice']
            camino_vertices = self.reconstruir_camino(prev, destino_v)
            camino_ids = [v.element() for v in camino_vertices]

            recargas, costo_real = self.calcular_paradas(camino_ids)

            resultado = {
                'orden': i,
                'origen': origen_nom,
                'destino': destino_nom,
                'ruta': camino_ids,
                'costo': costo_real,
                'recargas': recargas,
                'estado': 'Entregado'
            }
            self.estadisticas.append(resultado)

            #Informe
            print(f"---OrdeN--- #{i} de {origen_nom} a {destino_nom}")
            print("Ruta tomada:", " --> ".join(camino_ids))
            print(f"Costo total: {costo_real} | Recargas: {recargas} | Estado: Entregado\n")
