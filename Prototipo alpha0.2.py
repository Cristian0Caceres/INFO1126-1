import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
from main import recibir_datos_simulacion_nx
from graph import Graph
from route_manager import RouteManager

# Configuración de fuente para soportar emojis
mpl.rcParams['font.family'] = 'Segoe UI Emoji'

def draw_graph(G, pos, ax, highlight_path=None):
    node_colors = []
    for n in G.nodes():
        role = G.nodes[n].get('role', '👤 Cliente')
        if role == "📦 Almacenamiento":
            node_colors.append("orange")
        elif role == "🔋 Recarga":
            node_colors.append("cyan")
        else:
            node_colors.append("lightgreen")
    
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='lightgray', width=1, alpha=0.3)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)
    
    if highlight_path:
        path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3, ax=ax)
        nx.draw_networkx_nodes(G, pos, nodelist=highlight_path, node_color='purple', node_size=700, ax=ax)
        
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

def run_simulation_tab():
    st.header("🔄 Run Simulation")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        n_nodes = st.slider("Number of Nodes", 10, 150, 50, key="n_nodes")
    with col2:
        min_edges = max(n_nodes - 1, 10)
        m_edges = st.slider("Number of Edges", min_edges, 300, 100, key="m_edges")
    with col3:
        n_orders = st.slider("Number of Orders", 10, 300, 50, key="n_orders")
    
    n_storage = max(1, int(n_nodes * 0.2))
    n_recharge = max(1, int(n_nodes * 0.2))
    n_clients = max(1, n_nodes - n_storage - n_recharge)
    
    st.info(
        f"Node distribution:\n"
        f"- 📦 Storage: {n_storage} ({n_storage/n_nodes*100:.0f}%)\n"
        f"- 🔋 Recharge: {n_recharge} ({n_recharge/n_nodes*100:.0f}%)\n"
        f"- 👤 Clients: {n_clients} ({n_clients/n_nodes*100:.0f}%)"
    )
    
    if st.button("📊 Start Simulation"):
        if m_edges < n_nodes - 1:
            st.error("Number of edges must be at least n_nodes - 1 for a connected graph!")
            return
        
        aristas_iniciales = generar_arbol_aleatorio(n_nodes)
        G = nx.Graph()
        G.add_nodes_from(range(n_nodes))
        G.add_edges_from(aristas_iniciales)
        
        while G.number_of_edges() < m_edges:
            u, v = random.sample(range(n_nodes), 2)
            if not G.has_edge(u, v) and u != v:
                G.add_edge(u, v, weight=random.randint(1, 20))
        
        # Asignar letras a nodos: A, B, C...
        letras = [chr(ord('A') + i) for i in range(n_nodes)]
        mapping = dict(zip(G.nodes(), letras))
        G = nx.relabel_nodes(G, mapping)
        
        nodes = list(G.nodes())
        random.shuffle(nodes)
        
        roles = (
            ["📦 Almacenamiento"] * n_storage +
            ["🔋 Recarga"] * n_recharge +
            ["👤 Cliente"] * n_clients)
        random.shuffle(roles)
        
        role_map = {node: role for node, role in zip(nodes, roles)}
        nx.set_node_attributes(G, role_map, "role")
        
        st.success(
            f"Simulation started with:\n"
            f"- Nodes: {n_nodes}\n"
            f"- Edges: {m_edges}\n"
            f"- Orders: {n_orders}")
        
        role_colors = {
            "📦 Almacenamiento": "orange",
            "🔋 Recarga": "cyan", 
            "👤 Cliente": "lightgreen"}
        node_colors = [role_colors[G.nodes[n]['role']] for n in G.nodes]
        pos = nx.spring_layout(G, seed=42)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
        
        for role, color in role_colors.items():
            ax.scatter([], [], c=color, label=role)
        ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
        
        st.pyplot(fig)
        
        st.session_state['graph'] = G
        st.session_state['node_colors'] = node_colors
        st.session_state['pos'] = pos
        
        recibir_datos_simulacion_nx(G, n_orders)

def explore_network_tab():
    st.header("🔍 Explore Network")
    
    if 'graph' not in st.session_state:
        st.warning("Please generate a network first using the Run Simulation tab.")
        return
    
    G = st.session_state['graph']
    node_colors = st.session_state.get('node_colors', ['lightgreen']*len(G.nodes()))
    pos = st.session_state.get('pos', nx.spring_layout(G, seed=42))
    
    roles = nx.get_node_attributes(G, 'role')
    if not any(r == "📦 Almacenamiento" for r in roles.values()):
        st.error("Error: No storage nodes found in graph!")
        return
    if not any(r == "👤 Cliente" for r in roles.values()):
        st.error("Error: No client nodes found in graph!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Network Visualization")
        fig, ax = plt.subplots(figsize=(10, 8))
        
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
        
        role_colors = {
            "📦 Almacenamiento": "orange",
            "🔋 Recarga": "cyan",
            "👤 Cliente": "lightgreen"}
        for role, color in role_colors.items():
            ax.scatter([], [], c=color, label=role)
        ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("Route Calculator")
        nodes = list(G.nodes())
        node_labels = {n: f"{n} ({G.nodes[n]['role'][0]})" for n in nodes}
        
        origin = st.selectbox(
            "Select Origin Node", nodes, format_func=lambda x: node_labels[x], key="origin")
        destination = st.selectbox("Select Destination Node", nodes, format_func=lambda x: node_labels[x], key="destination")
        
        battery_limit = st.slider("Battery Limit", 10, 100, 50, key="battery_limit")
        
        if st.button("✈ Calculate Route"):
            if origin == destination:
                st.error("Origin and destination cannot be the same!")
            else:
                # Convertir grafo NetworkX a Graph (custom)
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
                
                path_edges = []
                for i in range(len(result['path'])-1):
                    u = result['path'][i]
                    v = result['path'][i+1]
                    if G.has_edge(u, v):
                        path_edges.append((u, v))
                
                fig, ax = plt.subplots(figsize=(10, 8))
                
                nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
                
                if path_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3, ax=ax)
                    nx.draw_networkx_nodes(G, pos, nodelist=result['path'], node_color='purple', node_size=700, ax=ax)
                
                nx.draw_networkx_nodes(G, pos, nodelist=[origin, destination], node_color=['blue', 'green'], node_size=700, ax=ax)
                
                ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
                st.pyplot(fig)
                
                if st.button("✅ Complete Delivery and Create Order"):
                    st.success("Order created successfully!")

def main():
    st.set_page_config(page_title="Drone Route Simulator", layout="wide")
    st.title("🚁 Drone Route Simulator with Recharge Stations")
    
    tab1, tab2 = st.tabs(["Run Simulation", "Explore Network"])
    
    with tab1:
        run_simulation_tab()
    
    with tab2:
        explore_network_tab()

if __name__ == "__main__":
    main()
