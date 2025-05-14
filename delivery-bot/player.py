from abc import ABC, abstractmethod
import heapq
from math import dist

from arrow import get

from route_optimizer import RouteOptimizer


class BasePlayer(ABC):
    def __init__(self, position):
        self.position = position
        self.cargo = 0
        self.battery = 70

    def dist(self, a, b):
        # Calcula a distância de Manhattan entre dois pontos a e b
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_dist(self, start, goal, world):
        maze = world.map
        size = world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        close_set = set()
        came_from = {}

        g_score = {tuple(start): 0}
        f_score = {tuple(start): self.dist(start, goal)}

        open_set = []
        heapq.heappush(open_set, (f_score[tuple(start)], tuple(start)))

        while open_set:
            _, current = heapq.heappop(open_set)
            
            if list(current) == goal:
                return g_score[current]  # retorna apenas a distância

            close_set.add(current)

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                tentative_g_score = g_score[current] + 1

                if 0 <= neighbor[0] < size and 0 <= neighbor[1] < size:
                    if maze[neighbor[1]][neighbor[0]] == 1:
                        continue
                else:
                    continue
                if neighbor in close_set:
                    continue

                if tentative_g_score < g_score.get(neighbor, float('inf')) or neighbor not in g_score:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.dist(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return float('inf')  # não há caminho possível

    @abstractmethod
    def escolher_alvo(self, world):
        pass

class DefaultPlayer(BasePlayer):
    def escolher_alvo(self, world):
        sx, sy = self.position
        if self.cargo == 0 and world.packages:
            best = None
            best_dist = float('inf')
            for pkg in world.packages:
                d = self.dist((sx, sy), pkg)
                if d < best_dist:
                    best_dist = d
                    best = pkg
            return best
        else:
            if world.goals:
                best = None
                best_dist = float('inf')
                for goal in world.goals:
                    d = self.dist((sx, sy), goal)
                    if d < best_dist:
                        best_dist = d
                        best = goal
                return best
            else:
                return None

class BatchCollectorPlayer(BasePlayer):
    def escolher_alvo(self, world):
        sx, sy = self.position

        # Etapa 1: Se há pacotes e o robô ainda pode carregar mais, continua coletando
        if world.packages:
            #return min(world.packages, key=lambda p: self.dist((sx, sy), p))
            return min(world.packages, key=lambda p: self.a_star_dist((sx, sy), p, world))
        
        # Etapa 2: Se está cheio ou não há mais pacotes, começa a entregar
        if world.goals:
            # return min(world.goals, key=lambda g: self.dist((sx, sy), g))
            return min(world.goals, key=lambda g: self.a_star_dist((sx, sy), g, world))
        
        # Etapa 3: Não há mais pacotes nem metas
        return None

class AdaptivePlayer(BasePlayer):
    def escolher_alvo(self, world):
        sx, sy = self.position
        targets = []

        if self.cargo == 0 and world.packages:
            targets = world.packages
        else:
            targets = list(world.packages) + list(world.goals)

        if not targets:
            return None
        
        #best = min(targets, key=lambda t: self.dist((sx, sy), t))
        best = min(targets, key=lambda t: self.a_star_dist((sx, sy), t, world))
        return best

class RechargerPlayer(AdaptivePlayer):
    def escolher_alvo(self, world):
        best = super().escolher_alvo(world) # pega o alvo mais próximo conforme a lógica do AdaptivePlayer
        
        if best is None: # guard clause para caso não tenha alvo
            return None
        
        sx, sy = self.position
        
        recharger = world.recharger
        if not recharger: # guard clause para caso não tenha recharger no mapa
            return best
        
        # dist_from_self_to_target = self.dist((sx, sy), best)
        # dist_from_target_to_recharger = self.dist(best, recharger)
        
        dist_from_self_to_target = self.a_star_dist((sx, sy), best, world)
        dist_from_target_to_recharger = self.a_star_dist(best, recharger, world)

        if (dist_from_self_to_target + dist_from_target_to_recharger > self.battery) or (dist_from_self_to_target > self.battery):
            return recharger

        return best
    
class OptimalPlayer(BasePlayer):
    def __init__(self, position):
        super().__init__(position)
        self.route = None
        self.fallback = None

    def escolher_alvo(self, world):
        if self.route is None:
            optimizer = RouteOptimizer(world, self.a_star_dist)
            self.route = optimizer.calculate_best_path(self.position)

            if self.route and self.route[0] == self.position:
                self.route = self.route[1:]

            if not self.route:
                self.fallback = RechargerPlayer(self.position)
        
        # Se há rota, segue-a
        if self.route:
            # remove e retorna o próximo nó do plano
            # print(self.route)
            return self.route.pop(0)

        # Senão, delega ao fallback
        return self.fallback.escolher_alvo(world)