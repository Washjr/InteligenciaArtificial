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
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()
        came_from = {}

        # fila de prioridade baseada apenas em h(n)
        open_heap = []
        open_set  = {tuple(start)}
        heapq.heappush(open_heap, (self.heuristic(start, goal), tuple(start)))

        while open_heap:
            _, current = heapq.heappop(open_heap)
            open_set.remove(current)
            if current in closed:
                continue
            closed.add(current)

            if list(current) == goal:
                # reconstrói o caminho
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path            

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                # só expande se estiver dentro do mapa e for transponível
                if not self.world.can_move_to(neighbor):
                    continue
                if neighbor in closed:
                    continue

                # registra de onde veio e empurra baseado só em h(neighbor, goal)
                if neighbor not in open_set:
                    came_from[neighbor] = current
                    open_set.add(neighbor)
                    heapq.heappush(open_heap, (self.heuristic(neighbor, goal), neighbor))

        # sem caminho
        return []
    
class DijkstraSearch(BaseSearch):
    def search(self, start, goal):        
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()
        came_from = {}

        # armazena o custo g(n) mínimo descoberto até cada nó
        g_score = {tuple(start): 0}
        
        # fila de prioridade baseada em g(n)
        open_heap = []
        heapq.heappush(open_heap, (0, tuple(start)))
        
        while open_heap:
            g_current, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            closed.add(current)
            
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

                # só expande se estiver dentro do mapa e for transponível
                if not self.world.can_move_to(neighbor):
                    continue
                if neighbor in closed:
                    continue                
                
                # custo para mover até 'neighbor'
                cost = self.world.cost_at(neighbor)
                g_neighbor = g_current + cost
                
                # se encontra caminho mais barato, atualiza e empurra na heap
                if g_neighbor < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = g_neighbor
                    came_from[neighbor] = current
                    heapq.heappush(open_heap, (g_neighbor, neighbor))
        
        # se não achou caminho
        return []
    
class GenericAStarSearch(BaseSearch):
    """
    Retorna o caminho de start a goal usando A* com f(n) = g(n) + weight * h(n).
    """
    def __init__(self, world, weight: float):
        super().__init__(world)
        self.weight = weight

    def search(self, start, goal):        
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()
        came_from = {}

        g_score = {tuple(start): 0}
        f_score = {tuple(start): self.weight * self.heuristic(start, goal)}

        open_heap = []
        heapq.heappush(open_heap, (f_score[tuple(start)], tuple(start)))

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            closed.add(current)

            if list(current) == goal:
                path = []
                while current in came_from:
                    path.append(list(current))
                    current = came_from[current]
                path.reverse()
                return path

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                if not self.world.can_move_to(neighbor):
                    continue   
                if neighbor in closed:
                    continue             

                # custo para mover até 'neighbor'
                cost = self.world.cost_at(neighbor)
                tentative_g = g_score[current] + cost

                # se encontrou caminho melhor, registra e empurra no heap
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.weight * self.heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (f_score[neighbor], neighbor))

        return []

class AStarSearch(GenericAStarSearch):
    """
    Peso = 1.0 para o A* clássico.
    """
    def __init__(self, world):        
        super().__init__(world, weight=1.0)


class WeightedAStarSearch(GenericAStarSearch):
    """
    Peso = 1.5 para o A* ponderado, priorizando heurística.
    """
    def __init__(self, world):        
        super().__init__(world, weight=1.5)