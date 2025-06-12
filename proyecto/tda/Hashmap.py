class HashMap:
    def __init__(self, size=10):
        self.size = size
        # Inicializa la tabla con una lista de listas para manejar colisiones mediante encadenamiento (chaining)
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        # Función hash sencilla que suma los códigos ASCII de los caracteres de la clave
        # y luego toma el módulo del tamaño de la tabla para obtener el índice
        return sum(ord(c) for c in key) % self.size

    def put(self, key, value):
        # Inserta o actualiza el valor asociado a la clave en el hashmap
        index = self._hash(key)  # Calcula el índice con la función hash
        for pair in self.table[index]:
            if pair[0] == key:
                # Si la clave ya existe, actualiza el valor y retorna
                pair[1] = value
                return
        # Si la clave no existe, agrega un nuevo par (clave, valor) en la lista del índice
        self.table[index].append([key, value])

    def get(self, key):
        # Obtiene el valor asociado a la clave, o None si no existe
        index = self._hash(key)  # Calcula el índice usando la función hash
        for pair in self.table[index]:
            if pair[0] == key:
                return pair[1]  # Retorna el valor encontrado
        return None  # No se encontró la clave

    def items(self):
        # Generador que recorre todas las claves y valores en la tabla
        for bucket in self.table:
            for key, value in bucket:
                yield key, value
