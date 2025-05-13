import heapq
import pygame
import random
from player import AdaptivePlayer

class World:
    def __init__(self, seed=None, render=True, player_class=AdaptivePlayer):
        if seed is not None:
            random.seed(seed)
        self.render = render
        self.maze_size = 30
        self.width = 600
        self.height = 600
        self.block_size = self.width // self.maze_size
        self.map = [[0 for _ in range(self.maze_size)] for _ in range(self.maze_size)]
        self.generate_obstacles()
        self.walls = []
        for row in range(self.maze_size):
            for col in range(self.maze_size):
                if self.map[row][col] == 1:
                    self.walls.append((col, row))
        self.total_items = 4
        self.packages = []
        while len(self.packages) < self.total_items + 1:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages:
                self.packages.append([x, y])
        self.goals = []
        while len(self.goals) < self.total_items:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.goals and [x, y] not in self.packages:
                self.goals.append([x, y])
        self.player = self.generate_player(player_class)
        self.recharger = self.generate_recharger()

        if self.render:
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

    def generate_obstacles(self):
        for _ in range(7):
            row = random.randint(5, self.maze_size - 6)
            start = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for col in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 1
        for _ in range(7):
            col = random.randint(5, self.maze_size - 6)
            start = random.randint(0, self.maze_size - 10)
            length = random.randint(5, 10)
            for row in range(start, start + length):
                if random.random() < 0.7:
                    self.map[row][col] = 1
        block_size = random.choice([4, 6])
        max_row = self.maze_size - block_size
        max_col = self.maze_size - block_size
        top_row = random.randint(0, max_row)
        top_col = random.randint(0, max_col)
        for r in range(top_row, top_row + block_size):
            for c in range(top_col, top_col + block_size):
                self.map[r][c] = 1

    def generate_player(self, player_class):
        while True:
            x = random.randint(0, self.maze_size - 1)
            y = random.randint(0, self.maze_size - 1)
            if self.map[y][x] == 0 and [x, y] not in self.packages and [x, y] not in self.goals:
                return player_class([x, y])

    # def generate_recharger(self):
    #     center = self.maze_size // 2
    #     candidates = []
    #     for dx in (-1, 0, +1):
    #         for dy in (-1, 0, +1):
    #             x, y = center + dx, center + dy
    #             if (0 <= x < self.maze_size and 0 <= y < self.maze_size
    #                 and self.map[y][x] == 0
    #                 and [x, y] not in self.packages
    #                 and [x, y] not in self.goals
    #                 and [x, y] != self.player.position):
    #                 candidates.append([x, y])
    #     if candidates:
    #         return random.choice(candidates)
        
    #     for y in range(self.maze_size):
    #         for x in range(self.maze_size):
    #             if (self.map[y][x] == 0
    #                 and [x, y] not in self.packages
    #                 and [x, y] not in self.goals
    #                 and [x, y] != self.player.position):
    #                 return [x, y]
                
    #     return None

    def generate_recharger(self):
        center = self.maze_size // 2

        # 1) tenta primeiro nas 9 células centrais (r = 0 e r = 1)
        candidates = []
        for dx in (-1, 0, +1):
            for dy in (-1, 0, +1):
                x, y = center + dx, center + dy
                if (0 <= x < self.maze_size and 0 <= y < self.maze_size
                    and self.map[y][x] == 0
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
                        and self.map[y][x] == 0
                        and [x, y] not in self.packages
                        and [x, y] not in self.goals
                        and [x, y] != self.player.position):
                        ring.append([x, y])

            if ring:
                return random.choice(ring)
                
        return None

    def can_move_to(self, pos):
        x, y = pos
        if 0 <= x < self.maze_size and 0 <= y < self.maze_size:
            return self.map[y][x] == 0
        return False

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
