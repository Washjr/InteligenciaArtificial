import itertools

class RouteOptimizer:
    """
    Resolve o problema de coletar 4 pacotes (entre N disponíveis) e fazer 4 entregas
    minimizando o número total de passos no grid, respeitando que sempre #coletas > #entregas.
    """
    def __init__(self, world, a_star_dist):
        self.world = world
        self.a_star_dist = a_star_dist

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

        FULL_MASK = (1 << n) - 1
        # dp[mask][i] = custo mínimo para visitar 'mask' e terminar em 'i'
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
        return path