import heapq
import pygame
from world import World

class Maze:
    def __init__(self, world, render=True):
        self.world = world
        self.debug = render
        self.running = True
        self.score = 0
        self.steps = 0
        self.delay = 100  # milissegundos entre movimentos
        self.path = []
        self.num_deliveries = 0  # contagem de entregas realizadas

    def heuristic(self, a, b):
        # Distância de Manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def astar(self, start, goal):
        maze = self.world.map
        size = self.world.maze_size
        neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        close_set = set()
        came_from = {}
        gscore = {tuple(start): 0}
        fscore = {tuple(start): self.heuristic(start, goal)}
        oheap = []
        heapq.heappush(oheap, (fscore[tuple(start)], tuple(start)))
        while oheap:
            current = heapq.heappop(oheap)[1]
            if list(current) == goal:
                data = []
                while current in came_from:
                    data.append(list(current))
                    current = came_from[current]
                data.reverse()
                return data
            close_set.add(current)
            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)
                tentative_g = gscore[current] + 1
                if 0 <= neighbor[0] < size and 0 <= neighbor[1] < size:
                    if maze[neighbor[1]][neighbor[0]] == 1:
                        continue
                else:
                    continue
                if neighbor in close_set and tentative_g >= gscore.get(neighbor, 0):
                    continue
                if tentative_g < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g
                    fscore[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return []

    def game_loop(self):
        # O jogo termina quando o número de entregas realizadas é igual ao total de itens.
        while self.running:
            if self.num_deliveries >= self.world.total_items:
                self.running = False
                break

            # Utiliza a estratégia do jogador para escolher o alvo
            target = self.world.player.escolher_alvo(self.world)
            if target is None:
                self.running = False
                break

            self.path = self.astar(self.world.player.position, target)
            if not self.path:
                #print("Nenhum caminho encontrado para o alvo", target)
                self.running = False
                break

            # Segue o caminho calculado
            for pos in self.path:
                self.world.player.position = pos
                self.steps += 1
                # Consumo da bateria: -1 por movimento se bateria >= 0, caso contrário -5
                self.world.player.battery -= 1
                if self.world.player.battery >= 0:
                    self.score -= 1
                else:
                    self.score -= 5
                # Recarrega a bateria se estiver no recharger
                if self.world.recharger and pos == self.world.recharger:
                    self.world.player.battery = 60
                    if(self.debug):
                        print("Bateria recarregada!")

                # Flag para escolher renderizar ou não pygame
                if self.debug:
                    self.world.draw_world(self.path)
                    pygame.time.wait(self.delay)

            # Ao chegar ao alvo, processa a coleta ou entrega:
            if self.world.player.position == target:
                # Se for local de coleta, pega o pacote.
                if target in self.world.packages:
                    self.world.player.cargo += 1
                    self.world.packages.remove(target)
                    #print("Pacote coletado em", target, "Cargo agora:", self.world.player.cargo)
                # Se for local de entrega e o jogador tiver pelo menos um pacote, entrega.
                elif target in self.world.goals and self.world.player.cargo > 0:
                    self.world.player.cargo -= 1
                    self.num_deliveries += 1
                    self.world.goals.remove(target)
                    self.score += 50
                    if(self.debug):
                        print("Pacote entregue em", target, "Cargo agora:", self.world.player.cargo)
            if(self.debug):
                print(f"Passos: {self.steps}, Pontuação: {self.score}, Cargo: {self.world.player.cargo}, Bateria: {self.world.player.battery}, Entregas: {self.num_deliveries}")

        if(self.debug):
            print("Fim de jogo!")
            print("Pontuação final:", self.score)
            print("Total de passos:", self.steps)
        
        # Flag para escolher renderizar ou não pygame
        if self.debug:
            pygame.quit()

        # **Retorna** o dicionário com as métricas
        return {
            "passos": self.steps,
            "score": self.score,
            "entregas": self.num_deliveries,
            "bateria": self.world.player.battery
        }
