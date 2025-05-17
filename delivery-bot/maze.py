import pygame
import time

class Maze:
    def __init__(self, world, search_strategy, render=True):
        self.world = world
        self.search_strategy = search_strategy  # Deve ser uma instância de BaseSearch
        self.debug = render
        self.running = True
        self.score = 0
        self.steps = 0
        self.delay = 100  # milissegundos entre movimentos
        self.path = []
        self.num_deliveries = 0  # contagem de entregas realizadas

        self.total_search_time = 0.0   # segundos
        self.search_calls      = 0

        self.negative_battery_count = 0

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

            t0 = time.perf_counter()
            self.path = self.search_strategy.search(self.world.player.position, target)
            t1 = time.perf_counter()

            self.total_search_time += (t1 - t0)
            self.search_calls += 1

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
                    self.negative_battery_count += 1

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
            "bateria": self.world.player.battery,
            "avg_search_time": (self.total_search_time / self.search_calls),
            "negative_battery_count": self.negative_battery_count
        }
