# proyecto2/api/controllers/summary.py

from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

# Simulaciones de ranking de visitas
fake_visits_clients = [
    {"client_id": 1, "name": "Ricardo Rios", "visits": 12},
    {"client_id": 2, "name": "Valeria Soto", "visits": 9},
    {"client_id": 3, "name": "Juan Torres", "visits": 4},
]

fake_visits_recharges = [
    {"node_id": 201, "visits": 20},
    {"node_id": 202, "visits": 14},
    {"node_id": 203, "visits": 8},
]

fake_visits_storages = [
    {"node_id": 101, "visits": 25},
    {"node_id": 102, "visits": 17},
    {"node_id": 103, "visits": 10},
]

fake_summary = {
    "total_clients": 3,
    "total_orders": 3,
    "total_recharges": 3,
    "total_storages": 3,
    "most_visited_client": "Ricardo Rios",
    "most_visited_storage": 101,
    "most_visited_recharge": 201,
}

@router.get("/visits/clients", response_model=List[Dict])
def get_clients_visit_ranking():
    return fake_visits_clients

@router.get("/visits/recharges", response_model=List[Dict])
def get_recharge_visit_ranking():
    return fake_visits_recharges

@router.get("/visits/storages", response_model=List[Dict])
def get_storage_visit_ranking():
    return fake_visits_storages

@router.get("/summary", response_model=Dict)
def get_summary():
    return fake_summary