# sim/simulation.py
import random
from collections import defaultdict
from model.graph import Graph
from domain.client import Client
from domain.order import Order
import datetime

class Simulation:
    def __init__(self):
        self.graph = Graph()
        self.clients = {}  # {client_id: Client}
        self.orders = {}   # {order_id: Order}
        self.node_visit_frequency = defaultdict(int)  # {node_id: visitas}
        self.node_type_count = {'cliente': 0, 'almacenamiento': 0, 'recarga': 0}
        self.is_active = False
        self.autonomy_limit = 50  # autonomía máxima del dron

        self._order_counter = 0
        self._client_counter = 0

    def generate_graph(self, num_nodes, num_edges):
        self.graph = Graph()
        roles = self._generate_roles(num_nodes)

        for i in range(num_nodes):
            node_id = f"N{i}"
            role = roles[i]
            self.graph.add_node(node_id, role)
            self.node_type_count[role] += 1

            # Si es cliente, creamos también un Client asociado
            if role == 'cliente':
                client_id = f"C{self._client_counter}"
                client = Client(client_id, f"Cliente_{client_id}", node_id)
                self.clients[client_id] = client
                self._client_counter += 1

        # Generar aristas aleatorias garantizando conectividad básica
        nodes_list = list(self.graph.all_nodes())

        # Aseguramos conectividad mínima (tipo árbol)
        for i in range(1, len(nodes_list)):
            peso = random.randint(1, 10)
            self.graph.add_edge(nodes_list[i - 1], nodes_list[i], peso)

        # Agregar aristas adicionales aleatorias hasta alcanzar num_edges
        while num_edges > len(nodes_list) - 1:
            n1, n2 = random.sample(nodes_list, 2)
            if n2 not in self.graph.get_neighbors(n1):
                peso = random.randint(1, 10)
                self.graph.add_edge(n1, n2, peso)
                num_edges -= 1

        self.is_active = True

    def _generate_roles(self, num_nodes):
        num_storage = int(num_nodes * 0.2)
        num_recharge = int(num_nodes * 0.2)
        num_clients = num_nodes - num_storage - num_recharge
        roles = ['almacenamiento'] * num_storage + ['recarga'] * num_recharge + ['cliente'] * num_clients
        random.shuffle(roles)
        return roles

    def register_node_visit(self, node_id):
        self.node_visit_frequency[node_id] += 1

    def create_order(self, client_id, origin, destination, cost=0):
        order_id = f"O{self._order_counter}"
        order = Order(order_id, self.clients[client_id], origin, destination)
        order.cost = cost
        self.orders[order_id] = order
        self.clients[client_id].add_order(order)
        self._order_counter += 1
        return order

    def get_node_roles_count(self):
        return self.node_type_count

    def complete_order(self, order, path_cost):
        order.complete(datetime.datetime.now(), path_cost)
        # Registrar visita a todos los nodos de ese trayecto (simulado por ahora)
        self.register_node_visit(order.origin)
        self.register_node_visit(order.destination)

    def reset(self):
        self.__init__()
