import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
from model.main import recibir_datos_simulacion_nx
from model.graph import Graph
from model.route_manager import RouteManager
import uuid
from datetime import datetime


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
        # 1) Generar grafo conectado
        if m_edges < n_nodes - 1:
            st.error("Number of edges must be at least n_nodes - 1 for a connected graph!")
            return
        
        aristas = generar_arbol_aleatorio(n_nodes)
        G = nx.Graph()
        G.add_nodes_from(range(n_nodes))
        G.add_edges_from(aristas)
        while G.number_of_edges() < m_edges:
            u, v = random.sample(range(n_nodes), 2)
            if u != v and not G.has_edge(u, v):
                G.add_edge(u, v, weight=random.randint(1, 20))
        
        # 2) Renombrar nodos a letras
        letras  = [chr(ord('A') + i) for i in range(n_nodes)]
        mapping = dict(zip(G.nodes(), letras))
        G = nx.relabel_nodes(G, mapping)
        
        # 3) Asignar roles aleatorios
        nodes = list(G.nodes())
        random.shuffle(nodes)
        roles = (["📦 Almacenamiento"] * n_storage +
                 ["🔋 Recarga"] * n_recharge +
                 ["👤 Cliente"] * n_clients)
        random.shuffle(roles)
        role_map = dict(zip(nodes, roles))
        nx.set_node_attributes(G, role_map, "role")
        
        # 4) Mostrar resumen y grafo
        st.success(f"Simulation started with:\n- Nodes: {n_nodes}\n- Edges: {m_edges}\n- Orders: {n_orders}")
        role_colors = {"📦 Almacenamiento":"orange","🔋 Recarga":"cyan","👤 Cliente":"lightgreen"}
        node_colors = [role_colors[G.nodes[n]['role']] for n in G.nodes()]
        pos = nx.spring_layout(G, seed=42)
        
        fig, ax = plt.subplots(figsize=(10,6))
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
        for role, color in role_colors.items():
            ax.scatter([], [], c=color, label=role)
        ax.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Node Types")
        st.pyplot(fig)
        
        # 5) Guardar estado básico
        st.session_state['graph']       = G
        st.session_state['node_colors'] = node_colors
        st.session_state['pos']         = pos
        
        # 6) Crear lista de clientes y mapeo nodo→cliente
        clients = []
        count = 1
        node_to_client = {}
        for node, data in G.nodes(data=True):
            if data['role'] == "👤 Cliente":
                client_id = f"C{count:03d}"
                clients.append({
                    "client_id":  client_id,
                    "name":       f"Client{count}",
                    "type":       "regular",
                    "total_orders": 0
                })
                node_to_client[node] = client_id
                count += 1
        
        st.session_state['clients']         = clients
        st.session_state['node_to_client']  = node_to_client
        
        # 7) Generar órdenes iniciales
        orders = []
        almacenes = [n for n,d in G.nodes(data=True) if d['role']=="📦 Almacenamiento"]
        clientes_nodos = [n for n,d in G.nodes(data=True) if d['role']=="👤 Cliente"]
        for _ in range(n_orders):
            origin      = random.choice(almacenes)
            destination = random.choice(clientes_nodos)
            
            # Reconstruir grafo custom y calcular ruta
            graph   = Graph(directed=False)
            node_map = {n: graph.insert_vertex(str(n)) for n in G.nodes()}
            for u, v, data in G.edges(data=True):
                graph.insert_edge(node_map[u], node_map[v], data.get("weight", 1))
            rm = RouteManager(graph)
            for n, data in G.nodes(data=True):
                if data['role'] == "🔋 Recarga":
                    rm.add_recharge_station(str(n))
            result = rm.find_route_with_recharge(str(origin), str(destination), battery_limit=100)  # o el límite que prefieras
            
            # Crear objeto orden
            order_id   = str(uuid.uuid4())
            created_at = datetime.now().isoformat()
            client_id  = node_to_client[destination]
            client_obj = next(c for c in clients if c['client_id']==client_id)
            client_obj['total_orders'] += 1
            
            orders.append({
                "order_id":     order_id,
                "client":       client_obj['name'],
                "client_id":    client_id,
                "origin":       origin,
                "destination":  destination,
                "status":       "pending",
                "priority":     0,
                "created_at":   created_at,
                "delivered_at": None,
                "route_cost":   result['total_cost']
            })
        
        st.session_state['orders'] = orders
        
        # 8) (Opcional) tus funciones de rendering de datos simulados
        recibir_datos_simulacion_nx(G, n_orders)

def explore_network_tab():
    st.header("🔍 Explore Network")
    if 'graph' not in st.session_state:
        st.warning("Genera primero la simulación en Run Simulation.")
        return

    G           = st.session_state['graph']
    node_colors = st.session_state['node_colors']
    pos         = st.session_state['pos']

    # --- Dibujo de la red ---
    fig, ax = plt.subplots(figsize=(8,6))
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
    st.pyplot(fig)

    # --- Panel de cálculo de ruta ---
    st.subheader("Route Calculator")
    nodes  = list(G.nodes())
    labels = {n: f"{n} ({G.nodes[n]['role'][0]})" for n in nodes}
    origin      = st.selectbox("Origin",      nodes, format_func=lambda x: labels[x], key="origin")
    destination = st.selectbox("Destination", nodes, format_func=lambda x: labels[x], key="destination")
    battery     = st.slider("Battery Limit", 10, 100, 50, key="battery_limit")

    # 1) Calcular y guardar última ruta
    if st.button("✈ Calculate Route", key="calc_route"):
        if origin == destination:
            st.error("Origin and destination cannot be the same!")
        else:
            # reconstruir grafo custom y calcular
            graph   = Graph(directed=False)
            node_map = {n: graph.insert_vertex(str(n)) for n in G.nodes()}
            for u,v,data in G.edges(data=True):
                graph.insert_edge(node_map[u], node_map[v], data.get("weight",1))
            rm = RouteManager(graph)
            for n,d in G.nodes(data=True):
                if d['role']=="🔋 Recarga":
                    rm.add_recharge_station(str(n))
            result = rm.find_route_with_recharge(str(origin), str(destination), battery)

            st.session_state['last_route'] = {
                "origin":      origin,
                "destination": destination,
                "result":      result
            }

    # 2) Mostrar última ruta y botón de entrega
    last = st.session_state.get('last_route')
    if last:
        ori = last['origin']
        dst = last['destination']
        res = last['result']

        st.success(f"**Path:** {' → '.join(res['path'])}")
        st.success(f"**Total Cost:** {res['total_cost']}")
        if res['recharge_stops']:
            st.info(f"**Recharge Stops:** {', '.join(res['recharge_stops'])}")

        # (Re)pinta la ruta
        fig2, ax2 = plt.subplots(figsize=(8,6))
        nx.draw(G, pos, ax=ax2, with_labels=True, node_color=node_colors, node_size=500)
        path_edges = [(res['path'][i], res['path'][i+1]) for i in range(len(res['path'])-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3, ax=ax2)
        st.pyplot(fig2)

        # 3) Botón para crear/actualizar orden
        if st.button("✅ Complete Delivery and Create Order", key="complete_delivery"):
            now_iso = datetime.now().isoformat()
            orders  = st.session_state.setdefault('orders', [])

            # buscar y actualizar orden pendiente
            for o in orders:
                if o['origin']==ori and o['destination']==dst and o.get('delivered_at') is None:
                    o['status']       = "delivered"
                    o['delivered_at'] = now_iso
                    break
            else:
                # si no existe, crear una nueva ya entregada
                client_id  = st.session_state['node_to_client'][dst]
                client_obj = next(c for c in st.session_state['clients']
                                  if c['client_id']==client_id)
                client_obj['total_orders'] += 1
                orders.append({
                    "order_id":     str(uuid.uuid4()),
                    "client":       client_obj['name'],
                    "client_id":    client_id,
                    "origin":       ori,
                    "destination":  dst,
                    "status":       "delivered",
                    "priority":     0,
                    "created_at":   now_iso,
                    "delivered_at": now_iso,
                    "route_cost":   res['total_cost']
                })

            st.success("Delivery registered!")

def clients_orders_tab():
    st.header("🌐 Clients & Orders")

    # 1) Mostrar clientes
    clients = st.session_state.get('clients', [])
    if not clients:
        st.warning("Ejecuta primero la simulación en Run Simulation.")
        return

    st.subheader("Clients")
    for c in clients:
        st.json(c)

    # 2) Mostrar siempre todas las órdenes, sin botones aquí
    orders = st.session_state.get('orders', [])
    st.subheader("Orders")
    if not orders:
        st.info("No se han generado órdenes aún.")
    else:
        for order in orders:
            st.json(order)

def main():
    st.set_page_config(page_title="Drone Route Simulator", layout="wide")
    st.title("🚁 Drone Route Simulator with Recharge Stations")
    
    tab1, tab2, tab3 = st.tabs(["Run Simulation", "Explore Network", "Clients & Orders"])
    
    with tab1:
        run_simulation_tab()
    
    with tab2:
        explore_network_tab()
    with tab3:
        clients_orders_tab()

if __name__ == "__main__":
    main()