from abc import ABC, abstractmethod

class BasePlayer(ABC):
    def __init__(self, position):
        self.position = position
        self.cargo = 0
        self.battery = 70

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
                d = abs(pkg[0] - sx) + abs(pkg[1] - sy)
                if d < best_dist:
                    best_dist = d
                    best = pkg
            return best
        else:
            if world.goals:
                best = None
                best_dist = float('inf')
                for goal in world.goals:
                    d = abs(goal[0] - sx) + abs(goal[1] - sy)
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
        best = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        return best

# class RechargerPlayer(BasePlayer):
#     def escolher_alvo(self, world):
        