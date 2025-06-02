class Edge:
    """Clase que representa una arista (conexión) entre dos vértices."""
    __slots__ = '_origin', '_destination', '_element'

    def __init__(self, u, v, x):
        """Inicializa la arista con dos vértices y un valor asociado."""
        self._origin = ____      # Vértice de origen
        self._destination = ____ # Vértice de destino
        self._element = ____     # Elemento asociado a la arista

    def endpoints(self):
        """Devuelve una tupla con los dos extremos de la arista (u, v)."""
        return (____, ____)  # Devolver _origin y _destination

    def opposite(self, v):
        """Devuelve el vértice opuesto a v en esta arista."""
        return ____ if v is self._origin else ____  # Retornar el opuesto

    def element(self):
        """Devuelve el valor asociado a esta arista."""
        return ____  # Retornar _element

    def __hash__(self):
        """Permite usar la arista como clave en estructuras tipo set/map."""
        return hash((____, ____))  # Usar _origin y _destination

    def __str__(self):
        """Representación en string de la arista."""
        return f"({____}->{____}):{____}"  # Usar origin, destination y element

    def __repr__(self):
        """Representación oficial de la arista."""
        return f"Edge({____}, {____}, {____})"  # Usar los atributos
