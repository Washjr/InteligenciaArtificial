from abc import ABC, abstractmethod
import heapq

class BaseSearch(ABC):
    def __init__(self, world):
        self.world = world

    def heuristic(self, a, b):
        # Distância de Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @abstractmethod
    def search(self, start, goal) -> list:
        pass
    
class GreedySearch(BaseSearch):
    def search(self, start, goal):
        maze = self.world.map
        size = self.world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()
        came_from = {}

        # fila de prioridade baseada apenas em h(n)
        open_heap = []
        heapq.heappush(open_heap, (self.heuristic(start, goal), tuple(start)))

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if list(current) == goal:
                # reconstrói o caminho
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path

            closed.add(current)

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                x, y = neighbor
                # dentro do mapa e não é parede
                if not (0 <= x < size and 0 <= y < size):
                    continue
                if maze[y][x] == 1:
                    continue

                if neighbor in closed:
                    continue

                # registra de onde viemos e empurra baseado só em h(neighbor, goal)
                if neighbor not in [n for _, n in open_heap]:
                    came_from[neighbor] = current
                    heapq.heappush(open_heap, (self.heuristic(neighbor, goal), neighbor))

        # sem caminho
        return []
    
class DijkstraSearch(BaseSearch):
    def search(self, start, goal):
        maze = self.world.map
        size = self.world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        visited = set()
        came_from = {}

        # dist guarda o custo g(n) mínimo descoberto até cada nó
        dist = {tuple(start): 0}
        
        # fila de prioridade baseada em g(n)
        open_heap = []
        heapq.heappush(open_heap, (0, tuple(start)))
        
        while open_heap:
            g_current, current = heapq.heappop(open_heap)
            if current in visited:
                continue
            visited.add(current)
            
            # ao alcançar o objetivo, reconstrói o caminho
            if list(current) == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path
            
            # expande vizinhos
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                x, y = neighbor
                # filtra fora do mapa ou paredes
                if not (0 <= x < size and 0 <= y < size):
                    continue
                if maze[y][x] == 1:
                    continue
                
                # custo para mover até 'neighbor'; aqui todo movimento custa 1
                g_neighbor = g_current + 1
                
                # se encontramos caminho mais barato, atualiza e empurra na heap
                if g_neighbor < dist.get(neighbor, float('inf')):
                    dist[neighbor] = g_neighbor
                    came_from[neighbor] = current
                    heapq.heappush(open_heap, (g_neighbor, neighbor))
        
        # se não achou caminho
        return []
    
class GenericAStarSearch(BaseSearch):
    """
    Retorna o caminho de start a goal usando A* com f = g + weight * h.
    """
    def __init__(self, world, weight: float):
        super().__init__(world)
        self.weight = weight

    def search(self, start, goal):
        maze = self.world.map
        size = self.world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()
        came_from = {}

        gscore = {tuple(start): 0}
        fscore = {tuple(start): self.weight * self.heuristic(start, goal)}

        open_heap = []
        heapq.heappush(open_heap, (fscore[tuple(start)], tuple(start)))

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if list(current) == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path

            closed.add(current)

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                tentative_g = gscore[current] + 1

                if 0 <= neighbor[0] < size and 0 <= neighbor[1] < size:
                    if maze[neighbor[1]][neighbor[0]] == 1:
                        continue
                else:
                    continue

                if neighbor in closed and tentative_g >= gscore.get(neighbor, float('inf')):
                    continue
                
                if tentative_g < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_heap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g
                    fscore[neighbor] = tentative_g + self.weight * self.heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (fscore[neighbor], neighbor))

        return []

class AStarSearch(GenericAStarSearch):
    """
    Peso = 1.0 para o A* clássico.
    """
    def __init__(self, world):        
        super().__init__(world, weight=1.0)


class WeightedAStarSearch(GenericAStarSearch):
    """
    Versão ponderada do A*: usa f(n) = g(n) + w * h(n), onde w é fixo em 1.5, para priorizar heurística.
    """
    def __init__(self, world):        
        super().__init__(world, weight=1.5)