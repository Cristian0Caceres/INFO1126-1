import heapq
from copy import deepcopy
from model.vertex import Vertex
from model.edge import Edge

class Graph:
    def __init__(self, directed=False):
        self._outgoing = {}
        self._incoming = {} if directed else self._outgoing
        self._directed = directed

    def is_directed(self):
        return self._directed

    def insert_vertex(self, element):
        v = Vertex(element)
        self._outgoing[v] = {}
        if self._directed:
            self._incoming[v] = {}
        return v

    def insert_edge(self, u, v, element):
        e = Edge(u, v, element)
        self._outgoing[u][v] = e
        self._incoming[v][u] = e
        return e

    def remove_edge(self, u, v):
        if u in self._outgoing and v in self._outgoing[u]:
            del self._outgoing[u][v]
            del self._incoming[v][u]

    def remove_vertex(self, v):
        for u in list(self._outgoing.get(v, {})):
            self.remove_edge(v, u)
        for u in list(self._incoming.get(v, {})):
            self.remove_edge(u, v)
        self._outgoing.pop(v, None)
        if self._directed:
            self._incoming.pop(v, None)

    def get_edge(self, u, v):
        return self._outgoing.get(u, {}).get(v)

    def vertices(self):
        return self._outgoing.keys()

    def edges(self):
        seen = set()
        for map in self._outgoing.values():
            seen.update(map.values())
        return seen

    def neighbors(self, v):
        return self._outgoing[v].keys()

    def degree(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return len(adj[v])

    def incident_edges(self, v, outgoing=True):
        adj = self._outgoing if outgoing else self._incoming
        return adj[v].values()


    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        yield start
        for neighbor in self.neighbors(start):
            if neighbor not in visited:
                yield from self.dfs(neighbor, visited)

    def bfs(self, start):
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            v = queue.pop(0)
            yield v
            for neighbor in self.neighbors(v):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    def topological_sort(self):
        in_degree = {v: 0 for v in self.vertices()}
        for u in self.vertices():
            for v in self.neighbors(u):
                in_degree[v] += 1

        queue = [v for v in self.vertices() if in_degree[v] == 0]
        result = []

        while queue:
            u = queue.pop(0)
            result.append(u)
            for v in self.neighbors(u):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(result) != len(in_degree):
            raise ValueError("Graph has a cycle. Topological sort not possible.")
        return result



##################################################################################
    def kruskal_mst(self):

        '''
            Kruskal's algorithm for finding the Minimum Spanning Tree (MST) of a graph.
            This implementation uses a union-find structure to efficiently manage connected components.
        1. Initialize a union-find structure to manage connected components.
        2. Sort all edges in non-decreasing order of their weight.  
        3. Iterate through the sorted edges and for each edge:
            a. Check if the endpoints of the edge belong to different components using the union-find structure.
            b. If they do, add the edge to the MST and union the components.
        4. Stop when the number of edges in the MST is equal to the number of vertices minus one.
        5. Return the edges in the MST.

        parameters:
            None

        returns:
            mst: A list of edges that form the Minimum Spanning Tree of the graph.
            '''
        parent = {}
        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]  
                v = parent[v]
            return v

        def union(u, v):
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[rv] = ru
                return True
            return False

        for v in self.vertices():
            parent[v] = v

      
        heap = [(e.element(), i, e) for i, e in enumerate(self.edges())]
        heapq.heapify(heap)

        mst = []
        while heap and len(mst) < len(parent) - 1:
            weight, _, edge = heapq.heappop(heap)
            u, v = edge.endpoints()
            if union(u, v):
                mst.append(edge)

        return mst

    # --- Algoritmo de Dijkstra usando heapq estándar ---
    def dijkstra_shortest_paths(self, src):
        '''
        Dijkstra's algorithm for finding the shortest paths from a source vertex to all other vertices in a weighted graph.
        This implementation uses a priority queue (min-heap) to efficiently retrieve the next vertex with the smallest distance.
        1. Initialize a distance dictionary with all vertices set to infinity, except the source vertex which is set to 0.
        2. Create a priority queue (min-heap) and add the source vertex with distance 0.
        3. While the heap is not empty:
            a. Pop the vertex with the smallest distance from the heap.
            b. If the vertex has already been visited, continue to the next iteration.  
            c. For each incident edge of the vertex, calculate the alternative distance to the opposite vertex.
            d. If the alternative distance is smaller than the current known distance, update the distance and 
                                                    add the opposite vertex to the heap with the new distance.
        4. Return the distance dictionary containing the shortest distances from the source vertex to all other vertices.

        
        parameters:
            src: The source vertex from which to calculate shortest paths.

        returns:
            dist: A dictionary mapping each vertex to its shortest distance from the source vertex.

        '''
        dist = {v: float('inf') for v in self.vertices()}
        dist[src] = 0
        heap = [(0, id(src), src)]
        visited = set()

        while heap:
            d, _, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            for e in self.incident_edges(u):
                v = e.opposite(u)
                if v not in visited:
                    alt = d + e.element()
                    if alt < dist[v]:
                        dist[v] = alt
                        heapq.heappush(heap, (alt, id(v), v))

        return dist

    # --- Algoritmo de Floyd-Warshall ---
    def floyd_warshall(self):
        '''
        Floyd-Warshall algorithm for finding the shortest paths between all pairs of vertices in a weighted graph.
        This implementation uses a dynamic programming approach to iteratively update the shortest paths.

        1. Initialize a distance dictionary with all pairs of vertices set to infinity, except for the diagonal (same vertex) which is set to 0.
        2. For each edge in the graph, set the distance between its endpoints to the
        weight of the edge.
        3. For each vertex k, iterate through all pairs of vertices (i, j) and update the distance from i to j if a shorter path through k is found.
        4. If a shorter path is found, update the distance and the edge in the graph.
        5. Return a new graph with the updated edges representing the shortest paths.
        

        parameters:
            None

        returns:
            closure: A new graph with the shortest paths between all pairs of vertices.
        
        '''
        closure = deepcopy(self)
        verts = list(closure.vertices())
        dist = { (u,v): float('inf') for u in verts for v in verts }
        for v in verts:
            dist[(v, v)] = 0
        for e in closure.edges():
            u, v = e.endpoints()
            dist[(u, v)] = e.element()

        for k in verts:
            for i in verts:
                for j in verts:
                    if dist[(i, j)] > dist[(i, k)] + dist[(k, j)]:
                        dist[(i, j)] = dist[(i, k)] + dist[(k, j)]
                        if closure.get_edge(i, j):
                            closure._outgoing[i][j]._element = dist[(i, j)]
                        else:
                            closure.insert_edge(i, j, dist[(i, j)])
        return closure

