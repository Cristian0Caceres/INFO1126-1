import streamlit as st
import networkx as nx
import random

st.title("🔄 Run Simulation")

# Sliders
n_nodes = st.slider("Número de Nodos", min_value=10, max_value=150, value=50)
m_edges = st.slider("Número de Aristas", min_value=10, max_value=300, value=100)
n_orders = st.slider("Número de Órdenes", min_value=10, max_value=300, value=50)

# Validación: al menos n_nodes - 1 aristas
if m_edges < n_nodes - 1:
    st.error("❗ El número de aristas debe ser al menos igual a Nodos - 1 para asegurar un grafo conexo.")
    st.stop()

# Botón de simulación
if st.button("📊 Start Simulation"):

    # Crear grafo conexo base
    G = nx.generators.random_tree(n_nodes)

    # Añadir aristas adicionales si es necesario
    current_edges = G.number_of_edges()
    while current_edges < m_edges:
        u, v = random.sample(range(n_nodes), 2)
        if not G.has_edge(u, v) and u != v:
            G.add_edge(u, v)
            current_edges += 1

    # Asignación de roles
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

    nx.set_node_attributes(G, {node: role for node, role in zip(nodes, roles)}, "role")

    # Campo informativo
    st.success(f"Nodos: {n_nodes} → Clientes: {n_clients} (60%), Almacenamiento: {n_storage} (20%), Recarga: {n_recharge} (20%)")

    # Mostrar grafo (opcional)
    try:
        import matplotlib.pyplot as plt
        role_colors = {"📦 Almacenamiento": "orange", "🔋 Recarga": "cyan", "👤 Cliente": "lightgreen"}
        color_map = [role_colors[G.nodes[n]['role']] for n in G.nodes]
        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=500, font_size=8)
        nx.draw_networkx_labels(G, pos, labels={n: G.nodes[n]['role'][0] for n in G.nodes}, font_color='black')
        st.pyplot(plt)
    except ImportError:
        st.warning("Instala matplotlib para visualizar el grafo.")

