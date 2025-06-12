# sim/dummy_simulator.py
from visual.avl_visualizer import AVLVisualizer
from tda.avl import AVLTree

# sim/dummy_simulator.py

def formatear_ruta(nodos):
    """Convierte una lista de nodos en una ruta tipo 'A → B → C'"""
    return " → ".join(nodos)

def obtener_rutas_simuladas():
    """
    Devuelve una lista de rutas simuladas (listas de nodos).
    Estas rutas son utilizadas para probar la pestaña de Route Analytics.
    """
    rutas = [
        ["A", "B", "C"],
        ["A", "B", "C"],
        ["A", "D", "E"],
        ["B", "F", "G"],
        ["A", "D", "E"],
        ["A", "B", "C"],
        ["H", "I"],
        ["B", "F", "G"],
        ["J", "K", "L"],
        ["A", "D", "E"],
    ]
    return rutas

# Si quieres probarlo directamente desde terminal
if __name__ == "__main__":
    from tda.avl import AVLTree

    rutas = obtener_rutas_simuladas()
    arbol = AVLTree()

    for ruta in rutas:
        ruta_str = formatear_ruta(ruta)
        arbol.insert_route(ruta_str)

    print("📋 Rutas en orden alfabético con frecuencia:")
    for ruta, freq in arbol.get_routes_inorder():
        print(f"{ruta} | Frecuencia: {freq}")
