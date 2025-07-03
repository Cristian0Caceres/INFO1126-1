# proyecto2/api/controllers/orders.py

from fastapi import APIRouter, HTTPException
from domain.order import Order
from typing import List
from datetime import datetime

router = APIRouter()

# Base de datos simulada temporal para pedidos
fake_orders_db = [
    Order(id=101, client_id=1, origin="A", destination="B", status="pendiente", 
          creation_date=datetime(2025, 6, 20), priority=1, delivery_date=None, total_cost=12.5),
    Order(id=102, client_id=2, origin="A", destination="C", status="completado", 
          creation_date=datetime(2025, 6, 21), priority=2, delivery_date=datetime(2025, 6, 22), total_cost=18.0),
    Order(id=103, client_id=1, origin="A", destination="D", status="pendiente", 
          creation_date=datetime(2025, 6, 22), priority=3, delivery_date=None, total_cost=9.75)
]

@router.get("/", response_model=List[Order])
def get_all_orders():
    return fake_orders_db

@router.get("/{order_id}", response_model=Order)
def get_order_by_id(order_id: int):
    for order in fake_orders_db:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Orden no encontrada")

@router.post("/{order_id}/cancel")
def cancel_order(order_id: int):
    for order in fake_orders_db:
        if order.id == order_id:
            if order.status == "pendiente":
                order.status = "cancelado"
                return {"message": f"Orden {order_id} cancelada exitosamente."}
            else:
                raise HTTPException(status_code=400, detail="La orden no puede ser cancelada")
    raise HTTPException(status_code=404, detail="Orden no encontrada")

@router.post("/{order_id}/complete")
def complete_order(order_id: int):
    for order in fake_orders_db:
        if order.id == order_id:
            if order.status == "pendiente":
                order.status = "completado"
                order.delivery_date = datetime.now()
                return {"message": f"Orden {order_id} completada exitosamente."}
            else:
                raise HTTPException(status_code=400, detail="La orden no puede ser completada")
    raise HTTPException(status_code=404, detail="Orden no encontrada")
