# domain/client.py

class Client:
    def __init__(self, client_id, name, node_id):
        self.client_id = client_id
        self.name = name
        self.node_id = node_id  # Nodo asociado en el grafo
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)
