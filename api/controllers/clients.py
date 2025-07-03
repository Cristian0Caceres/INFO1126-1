# proyecto2/api/controllers/clients.py

from fastapi import APIRouter, HTTPException
from domain.client import Client
from typing import List
from domain.client import Client
from fastapi import APIRouter, HTTPException
from domain.client import Client
from typing import List


router = APIRouter()

# Base de datos simulada temporal (puedes cambiar esto por HashMap luego)
fake_clients_db = [
    Client(id=1, name="Ricardo Rios", total_orders=3, type="👤 Cliente"),
    Client(id=2, name="Valeria Soto", total_orders=5, type="👤 Cliente"),
    Client(id=3, name="Juan Torres", total_orders=1, type="👤 Cliente")
]

@router.get("/", response_model=List[Client])
def get_all_clients():
    return fake_clients_db

@router.get("/{client_id}", response_model=Client)
def get_client_by_id(client_id: int):
    for client in fake_clients_db:
        if client.id == client_id:
            return client
    raise HTTPException(status_code=404, detail="Cliente no encontrado")


@router.get("/", response_model=List[Client])
def get_all_clients():
    return fake_clients_db
