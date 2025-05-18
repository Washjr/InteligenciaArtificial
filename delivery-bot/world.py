import pygame
import random
from player import AdaptivePlayer

class World:
    # custo de cada tipo de terreno
    TERRAIN_COSTS = {
        'P': 1,             # Plain (piso padrão)
        'S': 2,             # Slippery (piso escorregadio)
        'W': 3,             # Workshop (ferramentas no chão)
        'X': float('inf'),  # Wall (intransponível)
    }

    def __init__(self, seed=None, render=True, player_class=AdaptivePlayer):
        if seed is not None:
            random.seed(seed)

        self.render      = render
        self.maze_size   = 30
        self.width       = 600
        self.height      = 600
        self.block_size  = self.width // self.maze_size

        # Inicializa todo o mapa como piso padrão ('P')
        self.map = [['P' for _ in range(self.maze_size)] for _ in range(self.maze_size)]

        # Gera paredes ('X') e pisos especiais ('S') e ('W')
        self.generate_walls()
        self.generate_slippery_tiles()
        self.generate_workshop_tiles()

        # Coleta posições de paredes para desenho
        self.walls = []
        for row in range(self.maze_size):
            for col in range(self.maze_size):
                if self.map[row][col] == 'X':
                    self.walls.append((col, row))

        # Gera pacotes e destinos em células não‐paredes
        self.total_items = 4
        self.generate_packages()       
        self.generate_goals()       

        # Gera jogador e ponto de recarga
        self.player = self.generate_player(player_class)
        self.recharger = self.generate_recharger()

        # Flag para escolher renderizar ou não pygame
        if self.render:
            self.init_pygame()

    def generate_walls(self):        
        # Obstáculos horizontais
        for _ in range(7):
            row    = random.randint(5, self.maze_size - 6)
            start  = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for col in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 'X'

        # Obstáculos verticais
        for _ in range(7):
            col    = random.randint(5, self.maze_size - 6)
            start  = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for row in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 'X'

        # Obstáculos em bloco
        block_size = random.choice([4, 6])
        max_row = self.maze_size - block_size
        max_col = self.maze_size - block_size
        start_row = random.randint(0, max_row)
        start_col = random.randint(0, max_col)
        for row in range(start_row, start_row + block_size):
            for col in range(start_col, start_col + block_size):
                self.map[row][col] = 'X'

    def generate_slippery_tiles(self):
        # Gera pisos 'S' aleatoriamente
        for _ in range(50):
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 'P':
                self.map[y][x] = 'S'

    def generate_workshop_tiles(self):
        # Gera pisos 'W' aleatoriamente
        for _ in range(30):
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 'P':
                self.map[y][x] = 'W'

    def generate_packages(self):
        """
        Posiciona pacotes em células livres.
        """
        self.packages = []
        while len(self.packages) < self.total_items + 1:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] != 'X' and [x, y] not in self.packages:
                self.packages.append([x, y])            
                
    def generate_goals(self):
        """
        Posiciona destinos de entrega em células livres.
        """
        self.goals = []
        while len(self.goals) < self.total_items:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] != 'X' and [x, y] not in self.goals and [x, y] not in self.packages:
                self.goals.append([x, y])

    def generate_player(self, player_class):
        """
        Cria o jogador em uma célula livre.
        """
        while True:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] != 'X' and [x, y] not in self.packages and [x, y] not in self.goals:
                return player_class([x, y])

    def generate_recharger(self):
        """
        Encontra um ponto de recarga próximo ao centro, se possível.
        """ 
        center = self.maze_size // 2

        # 1) tenta primeiro nas 9 células centrais (r = 0 e r = 1)
        candidates = []
        for dx in (-1, 0, +1):
            for dy in (-1, 0, +1):
                x, y = center + dx, center + dy
                if (0 <= x < self.maze_size and 0 <= y < self.maze_size
                    and self.map[y][x] != 'X'
                    and [x, y] not in self.packages
                    and [x, y] not in self.goals
                    and [x, y] != self.player.position):
                    candidates.append([x, y])
        if candidates:
            return random.choice(candidates)
        
        # 2) expande o “anel” de raio r = 2, 3, … até o limite do grid
        max_radius = max(center, self.maze_size - center - 1)
        for r in range(2, max_radius + 1):
            ring = []
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    # só considera as células exatamente a “raio” r (anel)
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    
                    x, y = center + dx, center + dy
                    if (0 <= x < self.maze_size and 0 <= y < self.maze_size
                        and self.map[y][x] != 'X'
                        and [x, y] not in self.packages
                        and [x, y] not in self.goals
                        and [x, y] != self.player.position):
                        ring.append([x, y])
            if ring:
                return random.choice(ring)        
        return None

    def init_pygame(self):
        """
        Configurações iniciais do Pygame (tela, imagens, cores...).
        """
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Delivery Bot")
        self.package_image = pygame.image.load("images/cargo.png")
        self.package_image = pygame.transform.scale(self.package_image, (self.block_size, self.block_size))
        self.goal_image = pygame.image.load("images/operator.png")
        self.goal_image = pygame.transform.scale(self.goal_image, (self.block_size, self.block_size))
        self.recharger_image = pygame.image.load("images/charging-station.png")
        self.recharger_image = pygame.transform.scale(self.recharger_image, (self.block_size, self.block_size))
        self.wall_color = (100, 100, 100)
        self.ground_color = (255, 255, 255)
        self.player_color = (0, 255, 0)
        self.path_color = (200, 200, 0)

    def draw_world(self, path=None):
        self.screen.fill(self.ground_color)
        for (x, y) in self.walls:
            rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
            pygame.draw.rect(self.screen, self.wall_color, rect)
        for pkg in self.packages:
            x, y = pkg
            self.screen.blit(self.package_image, (x * self.block_size, y * self.block_size))
        for goal in self.goals:
            x, y = goal
            self.screen.blit(self.goal_image, (x * self.block_size, y * self.block_size))
        if self.recharger:
            x, y = self.recharger
            self.screen.blit(self.recharger_image, (x * self.block_size, y * self.block_size))
        if path:
            for pos in path:
                x, y = pos
                rect = pygame.Rect(x * self.block_size + self.block_size // 4,
                                   y * self.block_size + self.block_size // 4,
                                   self.block_size // 2, self.block_size // 2)
                pygame.draw.rect(self.screen, self.path_color, rect)
        x, y = self.player.position
        rect = pygame.Rect(x * self.block_size, y * self.block_size, self.block_size, self.block_size)
        pygame.draw.rect(self.screen, self.player_color, rect)
        pygame.display.flip()

    def cost_at(self, pos):
        x, y = pos
        terrain = self.map[y][x]
        return World.TERRAIN_COSTS[terrain]

    def can_move_to(self, pos):
        x, y = pos
        if 0 <= x < self.maze_size and 0 <= y < self.maze_size:
            return self.cost_at(pos) != float('inf')
        return False