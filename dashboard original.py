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
import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
import itertools
import string
import uuid
from datetime import datetime
from tda.avl import AVLTree




mpl.rcParams['font.family'] = 'Segoe UI Emoji'

ROLE_DISTRIBUTION = {
    "📦 Almacenamiento": 0.2,
    "🔋 Recarga": 0.2,
    "👤 Cliente": 0.6
}
ROLE_COLORS = {
    "📦 Almacenamiento": "orange",
    "🔋 Recarga": "cyan",
    "👤 Cliente": "lightgreen"
}


if "avl_tree" not in st.session_state:
    from tda.avl import AVLTree
    st.session_state.avl_tree = AVLTree()


def generar_nombres_nodos(n):
    letras = string.ascii_uppercase
    nombres = []
    for size in range(1, 4):
        for comb in itertools.product(letras, repeat=size):
            nombres.append(''.join(comb))
            if len(nombres) == n:
                return nombres
    return nombres[:n]

def generar_arbol_aleatorio(n):
    if n <= 1:
        return []
    prufer = [random.randint(0, n - 1) for _ in range(n - 2)]
    grado = [1] * n
    for nodo in prufer:
        grado[nodo] += 1
    aristas, hojas = [], sorted([i for i in range(n) if grado[i] == 1])
    for nodo in prufer:
        hoja = hojas.pop(0)
        aristas.append((hoja, nodo))
        grado[hoja] -= 1; grado[nodo] -= 1
        if grado[nodo] == 1:
            hojas.append(nodo); hojas.sort()
    u, v = [i for i in range(n) if grado[i] == 1]
    aristas.append((u, v))
    return aristas

def crear_grafo_con_roles(n_nodes, m_edges):
    aristas = generar_arbol_aleatorio(n_nodes)
    G = nx.Graph()
    G.add_nodes_from(range(n_nodes))
    G.add_edges_from(aristas)
    while G.number_of_edges() < m_edges:
        u, v = random.sample(range(n_nodes), 2)
        if u != v and not G.has_edge(u, v):
            G.add_edge(u, v, weight=random.randint(1, 20))
    nombres = generar_nombres_nodos(n_nodes)
    G = nx.relabel_nodes(G, dict(zip(G.nodes(), nombres)))
    roles, nodes = [], list(G.nodes())
    for role, perc in ROLE_DISTRIBUTION.items():
        roles += [role] * int(n_nodes * perc)
    roles += ["👤 Cliente"] * (n_nodes - len(roles))
    random.shuffle(roles)
    nx.set_node_attributes(G, dict(zip(nodes, roles)), "role")
    return G

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

    n_storage = max(1, int(n_nodes * ROLE_DISTRIBUTION["📦 Almacenamiento"]))
    n_recharge = max(1, int(n_nodes * ROLE_DISTRIBUTION["🔋 Recarga"]))
    n_clients = max(1, n_nodes - n_storage - n_recharge)

    st.info(f"Node distribution:\n- 📦 Storage: {n_storage} ({n_storage/n_nodes*100:.0f}%)\n- 🔋 Recharge: {n_recharge} ({n_recharge/n_nodes*100:.0f}%)\n- 👤 Clients: {n_clients} ({n_clients/n_nodes*100:.0f}%)")

    if st.button("📊 Start Simulation"):
        if m_edges < n_nodes - 1:
            st.error("Number of edges must be at least n_nodes - 1!")
            return

        G = crear_grafo_con_roles(n_nodes, m_edges)
        pos = nx.spring_layout(G, seed=42)
        node_colors = [ROLE_COLORS[G.nodes[n]['role']] for n in G.nodes()]
        st.session_state.update({'graph': G, 'pos': pos, 'node_colors': node_colors})

        # Crear clientes y mapping
        clients, node_to_client = [], {}
        count = 1
        for node, data in G.nodes(data=True):
            if data['role'] == "👤 Cliente":
                cid = f"C{count:03d}"
                clients.append({"client_id": cid, "name": f"Client{count}", "type": "regular", "total_orders": 0})
                node_to_client[node] = cid
                count += 1
        st.session_state['clients'] = clients
        st.session_state['node_to_client'] = node_to_client

        # Generar órdenes iniciales
        orders = []
        almacenes = [n for n,d in G.nodes(data=True) if d['role']=="📦 Almacenamiento"]
        clientes_nodos = list(node_to_client.keys())
        for _ in range(n_orders):
            origin = random.choice(almacenes)
            destination = random.choice(clientes_nodos)
            # calcular ruta
            graph = Graph(directed=False)
            nm = {n: graph.insert_vertex(str(n)) for n in G.nodes()}
            for u, v, data in G.edges(data=True):
                graph.insert_edge(nm[u], nm[v], data.get("weight",1))
            rm = RouteManager(graph)
            for n, d in G.nodes(data=True):
                if d['role']=="🔋 Recarga":
                    rm.add_recharge_station(str(n))
            res = rm.find_route_with_recharge(str(origin), str(destination), battery_limit=100)

            client_obj = next(c for c in clients if c['client_id']==node_to_client[destination])
            client_obj['total_orders'] += 1
            orders.append({
                "order_id": str(uuid.uuid4()),
                "client": client_obj['name'],
                "client_id": client_obj['client_id'],
                "origin": origin,
                "destination": destination,
                "status": "pending",
                "priority": 0,
                "created_at": datetime.now().isoformat(),
                "delivered_at": None,
                "route_cost": res['total_cost']
            })
        st.session_state['orders'] = orders
        recibir_datos_simulacion_nx(G, n_orders)
        st.success(f"Simulation started: Nodes={n_nodes}, Edges={m_edges}, Orders={n_orders}")

def explore_network_tab():
    st.header("🔍 Explore Network")
    if 'graph' not in st.session_state:
        st.warning("First run the simulation!")
        return
    G, pos, node_colors = st.session_state['graph'], st.session_state['pos'], st.session_state['node_colors']

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Network Visualization")
        fig, ax = plt.subplots(figsize=(10,8))
        nx.draw(G, pos, ax=ax, with_labels=True, node_color=node_colors, node_size=500)
        nx.draw_networkx_edge_labels(G, pos, {e: G.edges[e].get("weight",1) for e in G.edges()}, ax=ax)
        for role, color in ROLE_COLORS.items():
            ax.scatter([], [], c=color, label=role)
        ax.legend(title="Node Types", frameon=True)
        st.pyplot(fig)

    with col2:
        st.subheader("Route Calculator")
        nodes = list(G.nodes())
        labels = {n: f"{n} ({G.nodes[n]['role'][0]})" for n in nodes}
        origin = st.selectbox("Origin", nodes, format_func=lambda x: labels[x], key="origin")
        destination = st.selectbox("Destination", nodes, format_func=lambda x: labels[x], key="destination")
        battery_limit = st.slider("Battery Limit", 10, 100, 50, key="battery_limit")

        if st.button("✈ Calculate Route"):
            if origin == destination:
                st.error("Origin and destination cannot be the same!")
            else:
                graph = Graph(directed=False)
                nm = {n: graph.insert_vertex(str(n)) for n in G.nodes()}
                for u,v,data in G.edges(data=True):
                    graph.insert_edge(nm[u], nm[v], data.get("weight",1))
                rm = RouteManager(graph)
                for n,d in G.nodes(data=True):
                    if d['role']=="🔋 Recarga":
                        rm.add_recharge_station(str(n))
                res = rm.find_route_with_recharge(str(origin), str(destination), battery_limit=battery_limit)
                st.session_state['last_route'] = {"origin": origin, "destination": destination, "result": res}

        last = st.session_state.get('last_route')
        if last:
            ori, dst, res = last['origin'], last['destination'], last['result']
            st.success(f"Path: {' → '.join(res['path'])}")
            st.success(f"Total Cost: {res['total_cost']}")
            if res['recharge_stops']:
                st.info(f"Recharge stops: {', '.join(res['recharge_stops'])}")
            fig2, ax2 = plt.subplots(figsize=(10,8))
            nx.draw(G, pos, ax=ax2, with_labels=True, node_color=node_colors, node_size=500)
            path_edges = list(zip(res['path'][:-1], res['path'][1:]))
            nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=3, ax=ax2)
            st.pyplot(fig2)

            if st.button("✅ Complete Delivery and Create Order"):
                now_iso = datetime.now().isoformat()
                orders = st.session_state.setdefault('orders', [])
                updated = False
                for o in orders:
                    if o['origin']==ori and o['destination']==dst and o['delivered_at'] is None:
                        o['status'] = "delivered"
                        o['delivered_at'] = now_iso
                        updated = True
                        break
                if not updated:
                    client_id = st.session_state['node_to_client'][dst]
                    client_obj = next(c for c in st.session_state['clients'] if c['client_id']==client_id)
                    client_obj['total_orders'] += 1
                    orders.append({
                        "order_id": str(uuid.uuid4()),
                        "client": client_obj['name'],
                        "client_id": client_id,
                        "origin": ori,
                        "destination": dst,
                        "status": "delivered",
                        "priority": 0,
                        "created_at": now_iso,
                        "delivered_at": now_iso,
                        "route_cost": res['total_cost']
                    })
                st.success("Delivery registered!")

def clients_orders_tab():
    st.header("🌐 Clients & Orders")
    clients = st.session_state.get('clients')
    if not clients:
        st.warning("Run the simulation first!")
        return
    st.subheader("Clients")
    for c in clients:
        st.json(c)
    st.subheader("Orders")
    orders = st.session_state.get('orders', [])
    if not orders:
        st.info("No orders generated yet.")
    else:
        for o in orders:
            st.json(o)


def route_analytics_tab():
    st.header("📋 Route Analytics")

    if 'orders' not in st.session_state or not st.session_state['orders']:
        st.warning("Run the simulation first to generate routes.")
        return

    avl = st.session_state.get('avl_tree')
    if avl is None:
        st.error("AVL Tree not initialized.")
        return

    # Reiniciar el árbol manualmente (no hay método clear)
    avl.root = None

    # Contar frecuencia de rutas entre origen y destino
    route_freq = {}
    for order in st.session_state['orders']:
        route_key = f"{order['origin']} → {order['destination']}"
        route_freq[route_key] = route_freq.get(route_key, 0) + 1

    # Insertar rutas en AVLTree
    for route_key in route_freq:
        avl.insert_route(route_key)

    # Mostrar rutas ordenadas (in-order traversal)
    st.subheader("📄 Most Frequent Routes (AVL In-Order Traversal)")
    rutas = avl.get_routes_inorder()
    for ruta, freq in rutas:
        st.markdown(f"**{ruta}** — Freq: {freq}")

        # Visualización del árbol AVL
    st.subheader("🌳 AVL Tree Visualization")
    graph = nx.DiGraph()
    labels = {}
    construir_grafo_desde_avl(avl.root, graph, labels)

    if graph.number_of_nodes() == 0:
        st.info("No hay rutas registradas para graficar.")
        return

    pos = nx.spring_layout(graph, seed=42)
    fig, ax = plt.subplots(figsize=(12, 6))
    nx.draw(graph, pos, ax=ax, with_labels=True, labels=labels,
            node_size=2000, node_color='lightblue', font_size=10, font_weight='bold')
    st.pyplot(fig)



def construir_grafo_desde_avl(node, graph, labels, parent=None):
    if node is None:
        return
    nodo_id = f"{node.key}\nFreq: {node.freq}"
    graph.add_node(nodo_id)
    labels[nodo_id] = nodo_id
    if parent:
        graph.add_edge(parent, nodo_id)
    construir_grafo_desde_avl(node.left, graph, labels, nodo_id)
    construir_grafo_desde_avl(node.right, graph, labels, nodo_id)

def general_statistics_tab():
    st.header("📈 General Statistics")

    if 'graph' not in st.session_state or 'orders' not in st.session_state:
        st.warning("Run the simulation first to generate data.")
        return

    G = st.session_state['graph']
    orders = st.session_state['orders']

    # Contador de visitas por rol
    visit_counts = {
        "👤 Cliente": 0,
        "📦 Almacenamiento": 0,
        "🔋 Recarga": 0
    }

    for order in orders:
        origin_role = G.nodes[order['origin']]['role']
        destination_role = G.nodes[order['destination']]['role']
        visit_counts[origin_role] += 1
        visit_counts[destination_role] += 1

    # --- Gráfico de Barras: visitas por tipo de nodo ---
    st.subheader("📊 Nodo más visitado por tipo")
    fig1, ax1 = plt.subplots()
    roles = list(visit_counts.keys())
    counts = list(visit_counts.values())
    ax1.bar(roles, counts, color=['lightgreen', 'orange', 'cyan'])
    ax1.set_ylabel("Cantidad de visitas")
    ax1.set_title("Visitas a nodos por tipo")
    st.pyplot(fig1)

    # --- Gráfico de Torta: proporción de nodos por rol ---
    st.subheader("🥧 Proporción de nodos por rol")
    role_distribution = {"👤 Cliente": 0, "📦 Almacenamiento": 0, "🔋 Recarga": 0}
    for _, data in G.nodes(data=True):
        role_distribution[data['role']] += 1

    fig2, ax2 = plt.subplots()
    ax2.pie(role_distribution.values(), labels=role_distribution.keys(), autopct='%1.1f%%',
            colors=['lightgreen', 'orange', 'cyan'], startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)




def main():
    st.set_page_config(page_title="Drone Route Simulator", layout="wide")
    st.title("🚁 Drone Route Simulator with Recharge Stations")
    t1, t2, t3, t4, t5 = st.tabs(["Run Simulation", "Explore Network", "Clients & Orders", "📋 Route Analytics",  "📈 General Statistics"])
    with t1: run_simulation_tab()
    with t2: explore_network_tab()
    with t3: clients_orders_tab()
    with t4: route_analytics_tab()
    with t5: general_statistics_tab()



if __name__ == "__main__":
    main()