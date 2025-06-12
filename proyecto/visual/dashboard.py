# dashboard.py

import streamlit as st
from sim.dummy_simulator import obtener_rutas_simuladas
from tda.avl import AVLTree
from visual.avl_visualizer import AVLVisualizer
from sim.simulation import Simulation
import matplotlib.pyplot as plt
# Configuración general
st.set_page_config(page_title="Sistema Logístico con Drones", layout="wide")
st.title("📦 Sistema Logístico Autónomo con Drones")

# Crear simulación real si no existe aún
if 'simulation' not in st.session_state:
    st.session_state.simulation = Simulation()
    st.session_state.simulation.generate_graph(15, 20)  # Grafo inicial con 15 nodos, 20 aristas

# Barra lateral con pestañas
tabs = [
    "🔄 Run Simulation",
    "🌍 Explore Network",
    "🌐 Clients & Orders",
    "📋 Route Analytics",
    "📈 General Statistics"
]
selected_tab = st.sidebar.radio("Selecciona una pestaña", tabs)

# -------------------------
# PESTAÑA 4: Route Analytics
# -------------------------
if selected_tab == "📋 Route Analytics":
    st.header("📋 Route Analytics")
    st.markdown("Visualización de rutas más frecuentes utilizadas por los drones.")

    # Obtener rutas simuladas
    rutas_simuladas = obtener_rutas_simuladas()

    # Crear AVL e insertar rutas
    arbol = AVLTree()
    for ruta in rutas_simuladas:
        ruta_str = " → ".join(ruta)
        arbol.insert_route(ruta_str)

    # Mostrar rutas en orden
    st.subheader("📄 Rutas ordenadas con frecuencia:")
    rutas_ordenadas = arbol.get_routes_inorder()

    if rutas_ordenadas:
        for ruta, freq in rutas_ordenadas:
            st.text(f"{ruta} | Frecuencia: {freq}")
    else:
        st.warning("No hay rutas registradas.")

    # Visualización gráfica
    if st.button("📊 Visualizar Árbol AVL"):
        visualizador = AVLVisualizer()
        visualizador.draw(arbol.root)

# -------------------------
# PESTAÑA 5: General Statistics
# -------------------------
elif selected_tab == "📈 General Statistics":
    st.header("📈 General Statistics")

    simulation = st.session_state.simulation

    if not simulation or not simulation.is_active:
        st.warning("No hay simulación activa. Por favor, inicia una simulación.")
    else:
        nodos_visitados = simulation.node_visit_frequency
        nodos_tipos = simulation.get_node_roles_count()

        if not nodos_visitados:
            st.info("Todavía no hay datos de visitas a nodos. Genera rutas o pedidos para ver estadísticas.")
        else:
            # 📊 Gráfico de barras - Nodos más visitados
            st.subheader("🔝 Nodos más visitados")

            nodos_ordenados = sorted(nodos_visitados.items(), key=lambda x: x[1], reverse=True)[:10]  # Top 10
            labels = [str(node) for node, _ in nodos_ordenados]
            valores = [count for _, count in nodos_ordenados]

            fig, ax = plt.subplots()
            ax.bar(labels, valores, color='skyblue')
            ax.set_xlabel("ID Nodo")
            ax.set_ylabel("Cantidad de visitas")
            ax.set_title("Top 10 Nodos más visitados")
            st.pyplot(fig)

            # 🥧 Gráfico de torta - Proporción de tipos de nodos
            st.subheader("📊 Proporción de tipos de nodos")

            roles = list(nodos_tipos.keys())
            cantidades = list(nodos_tipos.values())

            fig2, ax2 = plt.subplots()
            ax2.pie(cantidades, labels=roles, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            st.pyplot(fig2)

# -------------------------
# Otras pestañas (vacías por ahora)
# -------------------------
elif selected_tab == "🔄 Run Simulation":
    st.info("Pestaña 1 - Run Simulation (a implementar)")

elif selected_tab == "🌍 Explore Network":
    st.info("Pestaña 2 - Explore Network (a implementar)")

elif selected_tab == "🌐 Clients & Orders":
    st.info("Pestaña 3 - Clients & Orders (a implementar)")
