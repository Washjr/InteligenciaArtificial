from abc import ABC, abstractmethod
import heapq

from route_optimizer import DefaultRouteOptimizer, RechargerRouteOptimizer

class BasePlayer(ABC):
    def __init__(self, position):
        self.position = position
        self.cargo = 0
        self.battery = 70

    def dist(self, a, b):
        # Calcula a distância de Manhattan entre dois pontos a e b
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def a_star_dist(self, start, goal, world):
        """
        Retorna o custo mínimo (soma de cost_at) para ir de start a goal,
        usando A* sobre world.can_move_to e world.cost_at.
        """        
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        closed = set()

        g_score = {tuple(start): 0}
        f_score = {tuple(start): self.dist(start, goal)}

        open_heap = []
        heapq.heappush(open_heap, (f_score[tuple(start)], tuple(start)))

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)
            
            if list(current) == goal:
                return g_score[current]  # retorna apenas a distância

            # Expande vizinhos válidos
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if not world.can_move_to(neighbor):
                    continue
                if neighbor in closed:
                    continue

                # custo para mover até 'neighbor'
                cost = world.cost_at(neighbor)
                tentative_g = g_score[current] + cost

                # se encontrou caminho melhor, registra e empurra no heap
                if tentative_g < g_score.get(neighbor, float('inf')):                    
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.dist(neighbor, goal)
                    heapq.heappush(open_heap, (f_score[neighbor], neighbor))

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

class DoubleBatchPlayer(BasePlayer):
    def __init__(self, position):
        super().__init__(position)
        self.collecting = True

    def escolher_alvo(self, world):
        sx, sy = self.position

        while True:
            # Modo coleta
            if self.collecting:
                if self.cargo < 2 and world.packages:                               
                    return min(world.packages, key=lambda p: self.a_star_dist((sx, sy), p, world))
                else:                
                    self.collecting = False
                    continue  # volta para a lógica de entrega no mesmo ciclo

            # Modo entrega
            if not self.collecting:
                if self.cargo > 0 and world.goals:                
                    return min(world.goals, key=lambda g: self.a_star_dist((sx, sy), g, world))
                else:                
                    self.collecting = True
                    continue  # volta para a lógica de coleta no mesmo ciclo

            return None

class FullBatchPlayer(BasePlayer):
    def escolher_alvo(self, world):
        sx, sy = self.position

        # Se há pacotes e o robô ainda pode carregar mais, continua coletando
        if world.packages:            
            return min(world.packages, key=lambda p: self.a_star_dist((sx, sy), p, world))
        
        # Se está cheio ou não há mais pacotes, começa a entregar
        if world.goals:            
            return min(world.goals, key=lambda g: self.a_star_dist((sx, sy), g, world))
        
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
        
        best = min(targets, key=lambda t: self.a_star_dist((sx, sy), t, world))
        return best

class ClusterAdaptivePlayer(BasePlayer):
    def __init__(self, position, radius=6, weight_distance=1.0, weight_cluster=2.0):
        super().__init__(position)        
        self.radius = radius
        self.weight_distance = weight_distance
        self.weight_cluster = weight_cluster

    def escolher_alvo(self, world):
        sx, sy = self.position
        targets = []

        def cluster_score(pos, targets):
            # Conta quantos outros alvos estão dentro do 'radius' de custo A* (e não é o próprio pos)
            return sum(
                1
                for t in targets
                if t != pos and self.dist(pos, t) <= self.radius
            )

        def cluster_heuristic(target, all_targets):
            dist = self.a_star_dist((sx, sy), target, world)
            cluster = cluster_score(target, all_targets)
            # quanto menor esse valor, mais atrativo
            return self.weight_distance * dist - self.weight_cluster * cluster

        # determina o conjunto de alvos conforme a carga
        if self.cargo == 0 and world.packages:
            targets = world.packages
        else:
            targets = list(world.packages) + list(world.goals)

        if not targets:
            return None

        # escolhe o alvo que minimiza a heurística de cluster
        return min(targets, key=lambda t: cluster_heuristic(t, targets))

class RechargerPlayer(AdaptivePlayer):
    def escolher_alvo(self, world):
        # pega o alvo mais próximo conforme a lógica do AdaptivePlayer
        best = super().escolher_alvo(world) 
        
        # guard clause para caso não tenha alvo
        if best is None: 
            return None
        
        sx, sy = self.position
        
        # guard clause para caso não tenha recharger no mapa
        recharger = world.recharger
        if not recharger: 
            return best
        
        # dist_from_self_to_target = self.dist((sx, sy), best)
        # dist_from_target_to_recharger = self.dist(best, recharger)
        
        dist_from_self_to_target = self.a_star_dist((sx, sy), best, world)
        dist_from_target_to_recharger = self.a_star_dist(best, recharger, world)

        if (dist_from_self_to_target + dist_from_target_to_recharger > self.battery) or (dist_from_self_to_target > self.battery):
            return recharger

        return best

class OptimizerPlayer(BasePlayer):
    """
    Player genérico que usa um RouteOptimizer para pré-planejar toda a rota,
    e um player de fallback caso não haja rota.
    """    
    def __init__(self, position, optimizer_cls, fallback_cls):
        super().__init__(position)
        self.optimizer_cls = optimizer_cls
        self.fallback_cls  = fallback_cls
        self.route = None
        self.fallback = None

    def escolher_alvo(self, world):
        if self.route is None:
            optimizer = self.optimizer_cls(world, self.a_star_dist)            
            self.route = optimizer.calculate_best_path(self.position)

            if not self.route:
                self.fallback = self.fallback_cls(self.position)
        
        # Se há rota, segue-a, senão delega ao fallback
        if self.route:
            return self.route.pop(0)
        else:
            return self.fallback.escolher_alvo(world)
    
class OptimalPlayer(OptimizerPlayer):
    """
    Usa DefaultRouteOptimizer para minimizar apenas o número de passos.
    """
    def __init__(self, position):        
        super().__init__(position,
                         optimizer_cls=DefaultRouteOptimizer,
                         fallback_cls=RechargerPlayer)

class OptimalRechargerPlayer(OptimizerPlayer):
    """
    Usa RechargerRouteOptimizer para otimizar considerando
    recarga de bateria e custo de passos com bateria negativa.
    """
    def __init__(self, position):        
        super().__init__(position,
                         optimizer_cls=RechargerRouteOptimizer,
                         fallback_cls=RechargerPlayer)