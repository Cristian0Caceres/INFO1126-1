from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Order(BaseModel):
    id: int
    client_id: int
    origin: str
    destination: str
    status: str
    creation_date: datetime
    priority: int
    delivery_date: Optional[datetime]
    total_cost: float
