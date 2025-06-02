class Vertex:
    """Clase que representa un vértice (nodo) en un grafo."""
    __slots__ = '_element'

    def __init__(self, element):
        """Inicializa el vértice con el elemento dado."""
        self._element = ____  # Asignar el valor del elemento recibido

    def element(self):
        """Devuelve el elemento asociado a este vértice."""
        return ____  # Retornar el valor almacenado en _element

    def __hash__(self):
        """Permite usar el vértice como clave en diccionarios o sets."""
        return hash(____)  # Usar id(self) para generar un hash único

    def __str__(self):
        """Devuelve la representación en string del vértice (su contenido)."""
        return ____  # Retornar el elemento como string

    def __repr__(self):
        """Representación oficial de la clase Vertex."""
        return f"Vertex({____})"  # Usar _element
