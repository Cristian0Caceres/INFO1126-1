import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
from main import recibir_datos_simulacion_nx
from graph import Graph
from route_manager import RouteManager

# Set font that supports emojis
mpl.rcParams['font.family'] = 'Segoe UI Emoji'

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

def explore_network_tab(G):
    st.header("🔍 Explore Network")
    
    # Verify required node types exist
    roles = nx.get_node_attributes(G, 'role')
    if not any(r == "📦 Almacenamiento" for r in roles.values()):
        st.error("Error: No warehouse nodes found in graph!")
        return
    if not any(r == "👤 Cliente" for r in roles.values()):
        st.error("Error: No client nodes found in graph!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Network Visualization")
        pos = nx.spring_layout(G, seed=42)
        role_colors = {
            "📦 Almacenamiento": "orange",
            "🔋 Recarga": "cyan",
            "👤 Cliente": "lightgreen"
        }
        node_colors = [role_colors[G.nodes[n]['role']] for n in G.nodes]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw(G, pos, ax=ax, with_labels=True, 
                node_color=node_colors, node_size=500)
        
        for role, color in role_colors.items():
            ax.scatter([], [], c=color, label=role)
        ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
        st.pyplot(fig)
    
    with col2:
        st.subheader("Route Calculator")
        nodes = list(G.nodes())
        node_labels = [f"{n} ({G.nodes[n]['role'][0]})" for n in nodes]
        
        origin = st.selectbox("Select Origin Node", nodes, format_func=lambda x: f"{x} ({G.nodes[x]['role'][0]})")
        destination = st.selectbox("Select Destination Node", nodes, format_func=lambda x: f"{x} ({G.nodes[x]['role'][0]})")
        
        battery_limit = st.slider("Battery Limit", 10, 100, 50)
        
        if st.button("✈ Calculate Route"):
            if origin == destination:
                st.error("Origin and destination cannot be the same!")
            else:
                try:
                    graph = Graph(directed=False)
                    node_map = {}
                    
                    for node in G.nodes:
                        v = graph.insert_vertex(str(node))
                        node_map[node] = v
                    
                    for u, v, data in G.edges(data=True):
                        weight = data.get("weight", 1)
                        graph.insert_edge(node_map[u], node_map[v], weight)
                    
                    route_manager = RouteManager(graph)
                    
                    for node, data in G.nodes(data=True):
                        if data.get("role") == "🔋 Recarga":
                            route_manager.add_recharge_station(str(node))
                    
                    result = route_manager.find_route_with_recharge(
                        str(origin), str(destination), battery_limit)
                    
                    st.success(f"**Path:** {' → '.join(result['path'])}")
                    st.success(f"**Total Cost:** {result['total_cost']}")
                    
                    if result['recharge_stops']:
                        st.info(f"**Recharge Stops:** {', '.join(result['recharge_stops'])}")
                    
                    path_edges = [(result['path'][i], result['path'][i+1]) 
                                for i in range(len(result['path'])-1)]
                    
                    fig, ax = plt.subplots(figsize=(10, 8))
                    nx.draw(G, pos, ax=ax, with_labels=True, 
                            node_color=node_colors, node_size=500)
                    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3, ax=ax)
                    nx.draw_networkx_nodes(G, pos, nodelist=[origin, destination], node_color=['purple', 'purple'], node_size=700, ax=ax)
                    ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
                    st.pyplot(fig)
                    
                    if st.button("✅ Complete Delivery and Create Order"):
                        st.success("Order created successfully!")
                
                except ValueError as e:
                    st.error(f"Error: {e}")

def main():
    st.set_page_config(page_title="Simulación de Rutas", layout="wide")
    st.title("🔄 Simulador de Rutas con Estaciones de Recarga")
    
    tab1, tab2 = st.tabs(["Simulation", "Explore Network"])
    
    with tab1:
        n_nodes = st.slider("Número de Nodos", 10, 150, 50)
        m_edges = st.slider("Número de Aristas", n_nodes - 1, 300, 100)
        n_orders = st.slider("Número de Órdenes", 10, 300, 50)
        
        if st.button("📊 Iniciar Simulación"):
            aristas_iniciales = generar_arbol_aleatorio(n_nodes)
            G = nx.Graph()
            G.add_nodes_from(range(n_nodes))
            G.add_edges_from(aristas_iniciales)
            
            while G.number_of_edges() < m_edges:
                u, v = random.sample(range(n_nodes), 2)
                if not G.has_edge(u, v) and u != v:
                    G.add_edge(u, v, weight=random.randint(1, 20))
            
            nodes = list(G.nodes())
            random.shuffle(nodes)
            
            # Ensure at least 1 of each type
            n_storage = max(1, int(n_nodes * 0.2))
            n_recharge = max(1, int(n_nodes * 0.2))
            n_clients = max(1, n_nodes - n_storage - n_recharge)
            
            roles = (
                ["📦 Almacenamiento"] * n_storage +
                ["🔋 Recarga"] * n_recharge +
                ["👤 Cliente"] * n_clients
            )
            random.shuffle(roles)
            
            role_map = {node: role for node, role in zip(nodes, roles)}
            nx.set_node_attributes(G, role_map, "role")
            
            st.success(f"Nodos: {n_nodes} → Clientes: {n_clients}, Almacenamiento: {n_storage}, Recarga: {n_recharge}")
            
            role_colors = {
                "📦 Almacenamiento": "orange",
                "🔋 Recarga": "cyan", 
                "👤 Cliente": "lightgreen"
            }
            node_colors = [role_colors[G.nodes[n]['role']] for n in G.nodes]
            pos = nx.spring_layout(G, seed=42)
            
            plt.figure(figsize=(10, 6))
            nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500)
            nx.draw_networkx_labels(G, pos, labels={n: G.nodes[n]['role'][0] for n in G.nodes}, font_color='black')
            st.pyplot(plt)
            
            st.session_state['graph'] = G
            recibir_datos_simulacion_nx(G, n_orders)
    
    with tab2:
        if 'graph' in st.session_state:
            explore_network_tab(st.session_state['graph'])
        else:
            st.warning("Please generate a network first using the Simulation tab.")

if __name__ == "__main__":
    main()