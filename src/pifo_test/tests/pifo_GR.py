class PIFO:
    def __init__(self):
        self.capacity = 16  # máximo número de elementos
        self.queue = []  # almacenará (rank, meta)
    
    def __iter__(self):
        return iter(self.queue)

    def is_full(self):
        return len(self.queue) >= self.capacity
    
    def is_empty(self):
        return len(self.queue) == 0
    
    def insert(self, rank_in, meta_in=None):
        """
        Inserta un nuevo elemento:
        - Si hay espacio, se inserta.
        - Si está lleno, solo reemplaza si el nuevo rank < max_rank().
        """
        if not self.is_full():
            # Hay espacio: insertar y ordenar por rank
            self.queue.append((rank_in, meta_in))
            self.queue.sort(key=lambda x: x[0])  # ordena por rank ascendente
            return True
        else:
            # Cola llena: checar si rank_in es menor que el máximo
            max_rank = max(self.queue, key=lambda x: x[0])[0]
            if rank_in < max_rank:
                # Reemplazar el elemento con el máximo rank
                max_idx = max(range(len(self.queue)), key=lambda i: self.queue[i][0])
                self.queue[max_idx] = (rank_in, meta_in)
                self.queue.sort(key=lambda x: x[0])
                return True
            else:
                # No se inserta porque tiene menor prioridad
                return False
    
    def remove(self):
        """
        Remove el elemento con el rank mínimo (frente de la cola).
        """
        if self.is_empty():
            return None
        return self.queue.pop(0)  # pop front (mínimo rank)
    
    def max_rank(self):
        if self.is_empty():
            return None
        return max(self.queue, key=lambda x: x[0])[0]
    
    def min_rank(self):
        if self.is_empty():
            return None
        return min(self.queue, key=lambda x: x[0])[0]
    
    def __repr__(self):
        return f"PIFO({self.queue})"

    def getQueue(self):
        return self.queue
