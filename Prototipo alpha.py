import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
from main import recibir_datos_simulacion_nx  # Asegúrate de que main.py esté en el mismo directorio

# Función para generar árbol aleatorio como lista de aristas (sin usar nx.random_tree)
def generar_arbol_aleatorio(n):
    if n <= 1:
        return []

    prufer = [random.randint(0, n - 1) for _ in range(n - 2)]
    grado = [1] * n
    for nodo in prufer:
        grado[nodo] += 1

    aristas = []
    hojas = sorted([i for i in range(n) if grado[i] == 1])

    for nodo in prufer:
        hoja = hojas.pop(0)
        aristas.append((hoja, nodo))
        grado[hoja] -= 1
        grado[nodo] -= 1
        if grado[nodo] == 1:
            hojas.append(nodo)
            hojas.sort()

    u, v = [i for i in range(n) if grado[i] == 1]
    aristas.append((u, v))
    return aristas

# Configuración de la página
st.set_page_config(page_title="Simulación de Rutas", layout="wide")
st.title("🔄 Simulador de Rutas con Estaciones de Recarga")

# Parámetros de simulación
n_nodes = st.slider("Número de Nodos", 10, 150, 50)
m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 100)
n_orders = st.slider("Número de Órdenes", 10, 300, 50)

# Botón de simulación
if st.button("📊 Iniciar Simulación"):
    # Crear árbol aleatorio base
    aristas_iniciales = generar_arbol_aleatorio(n_nodes)
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    G.add_edges_from(aristas_iniciales)

    # Añadir aristas adicionales si es necesario
    while G.number_of_edges() < m_edges:
        u, v = random.sample(range(n_nodes), 2)
        if not G.has_edge(u, v) and u != v:
            G.add_edge(u, v)

    # Asignar roles a los nodos
    nodes = list(G.nodes())
    random.shuffle(nodes)

    n_storage = int(n_nodes * 0.2)
    n_recharge = int(n_nodes * 0.2)
    n_clients = n_nodes - n_storage - n_recharge

    roles = (
        ["📦 Almacenamiento"] * n_storage +
        ["🔋 Recarga"] * n_recharge +
        ["👤 Cliente"] * n_clients
    )
    random.shuffle(roles)

    role_map = {node: role for node, role in zip(nodes, roles)}
    nx.set_node_attributes(G, role_map, "role")

    # Mostrar estadísticas
    st.success(f"Nodos: {n_nodes} → Clientes: {n_clients}, Almacenamiento: {n_storage}, Recarga: {n_recharge}")

    # Mostrar grafo
    role_colors = {"📦 Almacenamiento": "orange", "🔋 Recarga": "cyan", "👤 Cliente": "lightgreen"}
    node_colors = [role_colors[G.nodes[n]['role']] for n in G.nodes]
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500)
    nx.draw_networkx_labels(G, pos, labels={n: G.nodes[n]['role'][0] for n in G.nodes}, font_color='black')
    st.pyplot(plt)

    # Enviar datos a la lógica de rutas
    st.info("Buscando ruta óptima entre almacén y cliente...")
    recibir_datos_simulacion_nx(G, n_orders)
