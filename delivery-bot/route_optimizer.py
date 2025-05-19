import itertools
from abc import ABC, abstractmethod

class BaseRouteOptimizer(ABC):
    """
    Classe base para otimização de rotas em delivery-bot.
    Subclasses devem implementar `calculate_best_path(start_pos)`.
    """
    def __init__(self, world, a_star_dist):
        self.world = world
        self.a_star_dist = a_star_dist

    @abstractmethod
    def calculate_best_path(self, start_pos):
        """
        Retorna uma lista de posições (x,y) representando a ordem ótima de
        coleta/entrega (e recarga se aplicável).
        """
        pass

class DefaultRouteOptimizer(BaseRouteOptimizer):
    """
    Resolve o problema de coletar 4 pacotes (entre N disponíveis) e fazer 4 entregas
    minimizando o número total de passos no grid, respeitando que sempre #coletas > #entregas.

    OBS: Otimiza apenas o número de passos (sem considerar recarga/bateria).
    """
    
    def calculate_best_path(self, start_pos):
        # Monta lista de nós: [jogador] + pacotes + entregas
        nodes = [start_pos] + list(self.world.packages) + list(self.world.goals)
        n = len(nodes)
        # Índices
        start_idx = 0
        package_idxs = list(range(1, 1 + len(self.world.packages)))
        delivery_idxs = list(range(1 + len(self.world.packages), n))

        # Pré-computa matriz de distâncias par-a-par
        dist = [[float('inf')] * n for _ in range(n)]
        for i, j in itertools.permutations(range(n), 2):
            dist[i][j] = self.a_star_dist(nodes[i], nodes[j], self.world)

        # DP bitmask: dp[mask][i] = menor custo (passos) para visitar mask e terminar em i
        dp = [[float('inf')] * n for _ in range(1 << n)]
        dp[1 << start_idx][start_idx] = 0
        best_cost = float('inf')
        best_end = None

        for mask in range(1 << n):
            for i in range(n):
                if not (mask & (1 << i)): continue
                cost_i = dp[mask][i]
                if cost_i == float('inf'): continue

                # Conta coletas e entregas no estado atual
                n_collected = sum(1 for k in package_idxs if mask & (1 << k))
                n_delivered = sum(1 for k in delivery_idxs if mask & (1 << k))

                # Critério de parada: 4 coletas e 4 entregas
                if n_collected == 4 and n_delivered == 4:
                    if cost_i < best_cost:
                        best_cost = cost_i
                        best_end = (mask, i)
                    continue

                # Expande próximas transições
                for j in range(1, n):
                    if mask & (1 << j): continue
                    # Se j é entrega, só permite se houver pacote disponível
                    if j in delivery_idxs and n_collected <= n_delivered:
                        continue

                    new_mask = mask | (1 << j)
                    new_cost = cost_i + dist[i][j]
                    if new_cost < dp[new_mask][j]:
                        dp[new_mask][j] = new_cost

        # Reconstrução de caminho
        path = []
        if best_end:
            mask, i = best_end
            while True:
                path.append(nodes[i])
                if i == start_idx:
                    break
                # achar predecessor
                for k in range(n):
                    if k == i: continue
                    prev_mask = mask & ~(1 << i)
                    if prev_mask & (1 << k) and dp[prev_mask][k] + dist[k][i] == dp[mask][i]:
                        i = k
                        mask = prev_mask
                        break
            path.reverse()

        # remove a posição inicial
        if path and path[0] == start_pos:
            path.pop(0)

        return path
    

class RechargerRouteOptimizer(BaseRouteOptimizer):
    """
    Extende DefaultRouteOptimizer para incluir nó de recarga, bateria e custo em score.
    """
    def __init__(self, world, a_star_dist, battery_max=70, offset=100):
        super().__init__(world, a_star_dist)
        self.battery_max = battery_max
        self.offset = offset

    def calculate_best_path(self, start_pos):
        packages = list(self.world.packages)
        goals    = list(self.world.goals)
        recharge = self.world.recharger
        # jogador + pacotes + entregas + recarregador
        nodes = [start_pos] + packages + goals + [recharge]

        P, D = len(packages), len(goals)
        R = 1 + P + D
        n = len(nodes)

        # distâncias A*
        dist = [[self.a_star_dist(nodes[i], nodes[j], self.world) for j in range(n)] for i in range(n)]

        FULL = 1 << (1+P+D)
        BMAX = self.battery_max
        OFFSET = self.offset
        SIZE = BMAX + OFFSET + 1
        INF = float('inf')

        # dp[mask][i][b] = custo em penalidade (pontos perdidos)
        dp = [[[INF]*SIZE for _ in range(n)] for _ in range(FULL)]
        prev_state = [[[None] * SIZE for _ in range(n)] for _ in range(FULL)]

        # estado inicial: mask só com start, posição 0, bateria cheia (+ offset)
        dp[1][0][BMAX + OFFSET] = 0

        for mask in range(FULL):
            for i in range(n):
                for idx_b in range(SIZE):
                    C = dp[mask][i][idx_b]
                    if C == INF: continue

                    b_real = idx_b - OFFSET

                    collected = bin(mask & (((1<<P)-1)<<1)).count('1')
                    delivered = bin(mask & (((1<<D)-1)<<(1+P))).count('1')
                    if collected == 4 and delivered == 4:
                        continue

                    for j in range(1, n):
                        if mask & (1 << j):
                            continue  # já visitado

                        d = dist[i][j]
                        if d == INF: continue

                        # entrega só com carga
                        if 1+P <= j < 1+P+D and collected <= delivered:
                            continue

                        # calcula custo                        
                        extra = max(0, d - b_real)  # passos sem bateria
                        cost = C + (d - extra) * 1 + extra * 3

                        if j == R:                         
                            # Indo para o recarregador
                            nb_real = BMAX
                            nm = mask
                        else:
                            # Indo para outro ponto
                            nb_real = b_real - d
                            nm = mask | (1<<j)

                        idx_nb = nb_real + OFFSET

                        if 0 <= idx_nb < SIZE and cost < dp[nm][j][idx_nb]:
                            dp[nm][j][idx_nb] = cost
                            prev_state[nm][j][idx_nb] = (mask, i, idx_b)

        # seleciona melhor estado final
        best, state = INF, None
        for mask in range(FULL):
            if bin(mask & (((1<<P)-1)<<1)).count('1')==4 and bin(mask & (((1<<D)-1)<<(1+P))).count('1')==4:
                for i in range(n):
                    for idx_b in range(SIZE):
                        if dp[mask][i][idx_b] < best:
                            best = dp[mask][i][idx_b]
                            state = (mask, i, idx_b)                            
        if not state:
            return []

        # reconstrução
        mask, i, idx_b = state
        path = []

        while True:
            path.append(nodes[i])
            prev = prev_state[mask][i][idx_b]
            if prev is None:
                break
            mask, i, idx_b = prev

        path.reverse()

        # remove a posição inicial
        if path and path[0]==start_pos:
            path.pop(0)

        return path