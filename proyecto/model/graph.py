# model/graph.py

class Node:
    def __init__(self, node_id, role):
        """
        node_id: identificador único del nodo
        role: 'cliente', 'almacenamiento', o 'recarga'
        """
        self.id = node_id
        self.role = role
        self.edges = {}  # {destino: peso}

    def add_edge(self, destination, weight):
        self.edges[destination] = weight


class Graph:
    def __init__(self):
        self.nodes = {}  # {node_id: Node}

    def add_node(self, node_id, role):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, role)

    def add_edge(self, from_id, to_id, weight):
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].add_edge(to_id, weight)
            self.nodes[to_id].add_edge(from_id, weight)  # Asumimos grafo no dirigido

    def get_neighbors(self, node_id):
        if node_id in self.nodes:
            return self.nodes[node_id].edges
        return {}

    def get_node(self, node_id):
        return self.nodes.get(node_id, None)

    def all_nodes(self):
        return self.nodes.keys()

    def __contains__(self, node_id):
        return node_id in self.nodes
