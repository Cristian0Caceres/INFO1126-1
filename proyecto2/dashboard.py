import streamlit as st
import networkx as nx
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
import itertools
import string
import uuid
from datetime import datetime
import folium
from streamlit_folium import st_folium

from model.main import recibir_datos_simulacion_nx
from model.graph import Graph
from model.route_manager import RouteManager
from tda.avl import AVLTree

mpl.rcParams['font.family'] = 'Segoe UI Emoji'

ROLE_DISTRIBUTION = {
    "📦 Almacenamiento": 0.2,
    "🔋 Recarga": 0.2,
    "👤 Cliente": 0.6
}
ROLE_COLORS = {
    "📦 Almacenamiento": "orange",
    "🔋 Recarga": "cadetblue",
    "👤 Cliente": "green"
}

TEMUCO_BBOX = {
    'min_lat': -38.7450,
    'max_lat': -38.7250,
    'min_lon': -72.6250,
    'max_lon': -72.5900
}

if "avl_tree" not in st.session_state:
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

def generar_coordenadas_temporalmente_validas(n):
    puntos = []
    while len(puntos) < n:
        lat = random.uniform(TEMUCO_BBOX['min_lat'], TEMUCO_BBOX['max_lat'])
        lon = random.uniform(TEMUCO_BBOX['min_lon'], TEMUCO_BBOX['max_lon'])
        puntos.append((lat, lon))
    return puntos

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

    coords = generar_coordenadas_temporalmente_validas(n_nodes)
    for node, role, coord in zip(G.nodes(), roles, coords):
        G.nodes[node]["role"] = role
        G.nodes[node]["coord"] = coord

    return G

def mostrar_mapa_grafo_folium(G):
    fmap = folium.Map(location=[-38.735, -72.607], zoom_start=14)
    for node in G.nodes():
        data = G.nodes[node]
        coord = data.get("coord", (-38.735, -72.607))
        role = data.get("role", "👤 Cliente")
        color = ROLE_COLORS.get(role, "gray")

        folium.Marker(
            location=coord,
            popup=f"{node} - {role}",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(fmap)

    st_folium(fmap, width=1000, height=600)

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
        st.session_state['graph'] = G

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

        orders = []
        almacenes = [n for n,d in G.nodes(data=True) if d['role']=="📦 Almacenamiento"]
        clientes_nodos = list(node_to_client.keys())

        for _ in range(n_orders):
            origin = random.choice(almacenes)
            destination = random.choice(clientes_nodos)
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

    G = st.session_state['graph']

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
            for u, v, data in G.edges(data=True):
                graph.insert_edge(nm[u], nm[v], data.get("weight", 1))
            rm = RouteManager(graph)
            for n, d in G.nodes(data=True):
                if d['role'] == "🔋 Recarga":
                    rm.add_recharge_station(str(n))
            res = rm.find_route_with_recharge(str(origin), str(destination), battery_limit=battery_limit)
            st.session_state['last_route'] = {"origin": origin, "destination": destination, "result": res}

    last = st.session_state.get('last_route')

    # Crear mapa base
    fmap = folium.Map(location=[-38.735, -72.607], zoom_start=14)

    # Dibujar todas las aristas del grafo con tooltip del peso
    for u, v, data in G.edges(data=True):
        coord_u = G.nodes[u]['coord']
        coord_v = G.nodes[v]['coord']
        weight = data.get("weight", 1)
        tooltip = f"{u} ⇄ {v} — Peso: {weight}"
        folium.PolyLine(
            [coord_u, coord_v],
            color="gray",
            weight=2,
            opacity=0.6,
            tooltip=tooltip
        ).add_to(fmap)

    # Agregar nodos con iconos según rol usando emojis
    for node in G.nodes():
        data = G.nodes[node]
        coord = data.get("coord", (-38.735, -72.607))
        role = data.get("role", "👤 Cliente")
        emoji_icon = role[0]  # Primer carácter (emoji)
        folium.Marker(
            location=coord,
            popup=f"{node} - {role}",
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 24px; text-align: center; line-height: 24px;">{emoji_icon}</div>
            """)
        ).add_to(fmap)

    # Si hay ruta calculada, destacarla
    if last:
        ori, dst, res = last['origin'], last['destination'], last['result']
        st.success(f"Path: {' → '.join(res['path'])}")
        st.success(f"Total Cost: {res['total_cost']}")
        if res['recharge_stops']:
            st.info(f"Recharge stops: {', '.join(res['recharge_stops'])}")

        # Dibujar ruta calculada en rojo
        path_coords = [G.nodes[n]['coord'] for n in res['path']]
        folium.PolyLine(path_coords, color="red", weight=5, opacity=0.9, tooltip="Ruta óptima").add_to(fmap)

        # Marcar paradas de recarga
        for stop in res['recharge_stops']:
            coord = G.nodes[stop]['coord']
            folium.CircleMarker(
                location=coord,
                radius=8,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=f"🔋 Recarga: {stop}"
            ).add_to(fmap)

        # Registrar entrega
        if st.button("✅ Complete Delivery and Create Order"):
            now_iso = datetime.now().isoformat()
            orders = st.session_state.setdefault('orders', [])
            updated = False
            for o in orders:
                if o['origin'] == ori and o['destination'] == dst and o['delivered_at'] is None:
                    o['status'] = "delivered"
                    o['delivered_at'] = now_iso
                    updated = True
                    break
            if not updated:
                client_id = st.session_state['node_to_client'][dst]
                client_obj = next(c for c in st.session_state['clients'] if c['client_id'] == client_id)
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

                # Insertar en AVL Tree
                avl = st.session_state.get('avl_tree')
                if avl:
                    route_key = f"{ori} → {dst}"
                    avl.insert_route(route_key)

            st.success("Delivery registered!")

        # Botón para visualizar el dron moviéndose
        import time
        if st.button("🚁 Visualize Drone Moving"):
            for i, coord in enumerate(path_coords):
                fmap = folium.Map(location=coord, zoom_start=14)

                # Redibujar aristas
                for u, v, data in G.edges(data=True):
                    coord_u = G.nodes[u]['coord']
                    coord_v = G.nodes[v]['coord']
                    folium.PolyLine(
                        [coord_u, coord_v],
                        color="gray",
                        weight=2,
                        opacity=0.6
                    ).add_to(fmap)

                # Redibujar nodos con emojis
                for node in G.nodes():
                    data = G.nodes[node]
                    node_coord = data['coord']
                    role = data['role']
                    emoji_icon = role[0]
                    folium.Marker(
                        location=node_coord,
                        popup=f"{node} - {role}",
                        icon=folium.DivIcon(html=f"""
                            <div style="font-size: 24px; text-align: center; line-height: 24px;">{emoji_icon}</div>
                        """)
                    ).add_to(fmap)

                # Marcar posición actual del dron
                folium.Marker(
                    location=coord,
                    popup=f"🚁 Dron ({i+1}/{len(path_coords)})",
                    icon=folium.DivIcon(html="""
                        <div style="font-size:24px; color:red;">🚁</div>
                    """)
                ).add_to(fmap)

                st_folium(fmap, width=1000, height=600)
                time.sleep(0.5)

    # Mostrar el mapa con todo
    st.subheader("📍 Network Map")
    st_folium(fmap, width=1000, height=600)


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

def route_analytics_tab():
    st.header("📋 Route Analytics")
    if 'orders' not in st.session_state or not st.session_state['orders']:
        st.warning("Run the simulation first to generate routes.")
        return
    avl = st.session_state.get('avl_tree')
    if avl is None:
        st.error("AVL Tree not initialized.")
        return
    avl.root = None  # reset

    route_freq = {}
    for order in st.session_state['orders']:
        route_key = f"{order['origin']} → {order['destination']}"
        route_freq[route_key] = route_freq.get(route_key, 0) + 1

    for route_key in route_freq:
        avl.insert_route(route_key)

    st.subheader("📄 Most Frequent Routes (AVL In-Order Traversal)")
    rutas = avl.get_routes_inorder()
    for ruta, freq in rutas:
        st.markdown(f"**{ruta}** — Freq: {freq}")

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

def general_statistics_tab():
    st.header("📈 General Statistics")
    if 'graph' not in st.session_state or 'orders' not in st.session_state:
        st.warning("Run the simulation first to generate data.")
        return
    G = st.session_state['graph']
    orders = st.session_state['orders']

    visit_counts = {"👤 Cliente": 0, "📦 Almacenamiento": 0, "🔋 Recarga": 0}
    for order in orders:
        origin_role = G.nodes[order['origin']]['role']
        destination_role = G.nodes[order['destination']]['role']
        visit_counts[origin_role] += 1
        visit_counts[destination_role] += 1

    st.subheader("📊 Nodo más visitado por tipo")
    fig1, ax1 = plt.subplots()
    roles = list(visit_counts.keys())
    counts = list(visit_counts.values())
    ax1.bar(roles, counts, color=['green', 'orange', 'cadetblue'])
    ax1.set_ylabel("Cantidad de visitas")
    ax1.set_title("Visitas a nodos por tipo")
    st.pyplot(fig1)

    st.subheader("🥧 Proporción de nodos por rol")
    role_distribution = {"👤 Cliente": 0, "📦 Almacenamiento": 0, "🔋 Recarga": 0}
    for _, data in G.nodes(data=True):
        role_distribution[data['role']] += 1

    fig2, ax2 = plt.subplots()
    ax2.pie(role_distribution.values(), labels=role_distribution.keys(), autopct='%1.1f%%',
            colors=['green', 'orange', 'cadetblue'], startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)

def main():
    st.set_page_config(page_title="Drone Route Simulator", layout="wide")
    st.title("🚁 Drone Route Simulator with Recharge Stations")
    tabs = st.tabs([
        "Run Simulation",
        "Explore Network",
        "Clients & Orders",
        "📋 Route Analytics",
        "📈 General Statistics"
    ])

    with tabs[0]:
        run_simulation_tab()
    with tabs[1]:
        explore_network_tab()
    with tabs[2]:
        clients_orders_tab()
    with tabs[3]:
        route_analytics_tab()
    with tabs[4]:
        general_statistics_tab()

if __name__ == "__main__":
    main()
