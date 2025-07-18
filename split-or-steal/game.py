import pygame
import numpy as np
from itertools import combinations
from collections import defaultdict

MEAN = 100
VARIANCE = 10000
# IMAGE_PATH = 'split-or-steal/images'
IMAGE_PATH = 'images'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Game:
    def __init__(self, total_rounds, render=False):
        self.render = render
        self.total_rounds = total_rounds 
        self.rounds_played = 0
        self.current_amount = 0 

        if self.render:
            # Inicialização do Pygame e configuração visual
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Split or Steal")

            # Carrega e escalona imagens
            image_scale = 0.5            
            self.split_img = pygame.transform.scale(
                pygame.image.load(f"{IMAGE_PATH}/split.png"), 
                (int(196 * image_scale), int(128 * image_scale))
            )
            self.steal_img = pygame.transform.scale(
                pygame.image.load(f"{IMAGE_PATH}/steal.png"), 
                (int(196 * image_scale), int(128 * image_scale))
            )
            self.doubt_img = pygame.transform.scale(
                pygame.image.load(f"{IMAGE_PATH}/card_back.png"), 
                (int(196 * image_scale), int(128 * image_scale))
            )
            self.background = pygame.transform.scale(
                pygame.image.load(f"{IMAGE_PATH}/background.png"),
                (SCREEN_WIDTH, SCREEN_HEIGHT)
            )

            # Fonte
            self.font = pygame.font.SysFont(None, 24)
            self.big_font = pygame.font.Font(None, 72)

    def is_over(self) -> bool:
        return self.rounds_played >= self.total_rounds

    def prepare_round(self) -> None:
        """Define o valor atual da rodada com distribuição normal."""
        self.current_amount = max(MEAN, np.random.normal(MEAN, np.sqrt(VARIANCE)))

    def play_round(self, left_player, right_player, remaining_rounds):
        self.rounds_played += 1

        # Decisões
        left_decision = left_player.decision(self.current_amount, remaining_rounds, left_player.karma, right_player.karma)
        right_decision = right_player.decision(self.current_amount, remaining_rounds, right_player.karma, left_player.karma)
        assert left_decision in ("split", "steal") and right_decision in ("split", "steal")

        print(f"Player {left_player.name}={left_decision}"
              f" vs Player {right_player.name}={right_decision}")

        # Cálculo das recompensas
        if left_decision == right_decision == "steal":
            left_reward = 0
            right_reward = 0
        elif left_decision == right_decision == "split":
            left_reward = self.current_amount / 2
            right_reward = self.current_amount / 2  
        elif left_decision == "steal":
            left_reward = self.current_amount   
            right_reward = 0  
        else:
            left_reward = 0
            right_reward = self.current_amount 

        print(f"Player {left_player.name} ganhou {left_reward:.2f}"
              f" vs Player {right_player.name} ganhou {right_reward:.2f}")

        # Atualiza estados e karma
        left_player.total_amount += left_reward
        right_player.total_amount += right_reward

        left_player.result(left_decision, right_decision, self.current_amount, left_reward)
        right_player.result(right_decision, left_decision, self.current_amount, right_reward)

        left_player.add_karma(1 if left_decision == "split" else -1)
        right_player.add_karma(1 if right_decision == "split" else -1)

        # Retorna recompensas para uso externo
        return left_reward, right_reward


    # Métodos de renderização
    def _render_common(self) -> None:
        """Preenche tela e desenha o cabeçalho de rodadas."""
        self.screen.fill(BLACK)
        self.screen.blit(self.background, (0, 0))

        rounds_text = self.font.render(
            f"Rodadas: {self.rounds_played}/{self.total_rounds}", True, BLACK
        )
        self.screen.blit(rounds_text, (320, 50))

    def render_start(self) -> None:
        """Renderiza informações pré-decisão (rodada e valor)."""
        self._render_common()
        amount_text = self.big_font.render(
            f"$ {self.current_amount:.2f}", True, BLACK
        )
        self.screen.blit(amount_text, (350, 200))

    def render_end(self) -> None:
        """Renderiza após a decisão."""
        self._render_common()
        


    def _draw_player(self, player, x, y):
        pygame.draw.rect(self.screen, BLACK, (x, y, 200, 80))
        self.screen.blit(self.font.render(player.name, True, WHITE), (x+10, y+10))
        self.screen.blit(self.font.render(f"Amount: {player.total_amount:.2f}", True, WHITE), (x+10, y+30))
        self.screen.blit(self.font.render(f"Karma: {player.karma}", True, WHITE), (x+10, y+50))

    def draw_player_preround(self, player, x, y) -> None:
        self._draw_player(player, x, y)
        self.screen.blit(self.doubt_img, (x+150, y+10))

    def draw_player_postround(self, player, x, y) -> None:
        self._draw_player(player, x, y)
        img = self.split_img if player.last_decision=='split' else self.steal_img
        self.screen.blit(img, (x+150, y+10))



    

    def update_display(self) -> None:
        """Atualiza o display e pausa brevemente para controlar a velocidade."""
        pygame.display.flip()

        # pausa total de ~4 ms; ajuste para 100 ms se quiser rodar mais devagar
        for _ in range(4):
            pygame.time.wait(1)

    def handle_events(self) -> None:
        """Processa eventos do Pygame e encerra se necessário."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()