from abc import ABC, abstractmethod
from math import dist

from arrow import get

class BasePlayer(ABC):
    def __init__(self, position):
        self.position = position
        self.cargo = 0
        self.battery = 70

    def dist(self, a, b):
        # Calcula a distância de Manhattan entre dois pontos a e b
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

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
        best = min(targets, key=lambda t: self.dist((sx, sy), t))
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
        
        dist_to_target = self.dist((sx, sy), best)
        dist_to_recharger = self.dist(best, recharger)

        if (dist_to_target + dist_to_recharger > self.battery) or (dist_to_target > self.battery):
            return recharger

        return best

