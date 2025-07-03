# proyecto2/domain/client.py

from pydantic import BaseModel

class Client(BaseModel):
    id: int
    name: str
    total_orders: int
    type: str
