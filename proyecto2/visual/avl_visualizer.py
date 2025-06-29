import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

class AVLVisualizer:
    def __init__(self):
        self.G = nx.DiGraph()
        self.pos = {}
        self.labels = {}

    def build_graph(self, node, x=0, y=0, dx=1.0):
        if not node:
            return
        node_id = id(node)
        label = f"{node.key}\nFreq: {node.freq}"
        self.G.add_node(node_id)
        self.labels[node_id] = label
        self.pos[node_id] = (x, y)
        if node.left:
            self.G.add_edge(node_id, id(node.left))
            self.build_graph(node.left, x - dx, y - 1, dx / 1.5)
        if node.right:
            self.G.add_edge(node_id, id(node.right))
            self.build_graph(node.right, x + dx, y - 1, dx / 1.5)

    def draw(self, root):
        self.G.clear()
        self.labels.clear()
        self.pos.clear()
        self.build_graph(root)

        fig, ax = plt.subplots(figsize=(12, 6))
        nx.draw(
            self.G,
            pos=self.pos,
            labels=self.labels,
            with_labels=True,
            node_color="skyblue",
            node_size=2500,
            font_size=10,
            ax=ax
        )
        plt.title("Visualización del Árbol AVL de Rutas")
        plt.axis('off')
        st.pyplot(fig)  # 🔥 esto reemplaza plt.show()
