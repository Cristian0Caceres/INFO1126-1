# domain/order.py
import datetime

class Order:
    def __init__(self, order_id, client, origin, destination, priority=1):
        self.order_id = order_id
        self.client = client
        self.origin = origin
        self.destination = destination
        self.priority = priority
        self.status = "pending"
        self.created_at = datetime.datetime.now()
        self.delivered_at = None
        self.cost = 0  # Se calculará según el camino

    def complete(self, delivery_time, cost):
        self.status = "delivered"
        self.delivered_at = delivery_time
        self.cost = cost
