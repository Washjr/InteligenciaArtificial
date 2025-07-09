import pygame
import random
import numpy as np  
from itertools import permutations, combinations
import simple_opponents
import your_agent
import rl_agent

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Split or Steal")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Load images
split_img = pygame.image.load('split.png')
steal_img = pygame.image.load('steal.png')
doubt_img = pygame.image.load('card_back.png')
background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
# Scale images
image_scale = 0.5
split_img = pygame.transform.scale(split_img, (int(196 * image_scale), int(128 * image_scale)))
steal_img = pygame.transform.scale(steal_img, (int(196 * image_scale), int(128 * image_scale)))
doubt_img = pygame.transform.scale(doubt_img, (int(196 * image_scale), int(128 * image_scale)))

mean = 100
variance = 10000  # Large variance

# Fonts
font = pygame.font.SysFont(None, 24)

# Game settings
rounds_to_play = 10

class Game:
    def __init__ (self, total_rounds):
        self.rounds_played = 0
        self.total_rounds = total_rounds 
        self.current_amount = 0 
        
    def isOver(self):
        return self.rounds_played >= self.total_rounds;    
        
    def prepare_round(self):
        # Generate random values for total amount and rounds played
        self.current_amount = max(mean, np.random.normal(mean, np.sqrt(variance)))    
         
    
    def play_round(self, left_agent, right_agent, remaining):  
        self.rounds_played += 1


        # Call the callback function with the generated values
        left_decision = left_agent.decision(self.current_amount, remaining, left_agent.karma, right_agent.karma)
        assert left_decision in ["split", "steal"]
        right_decision = right_agent.decision(self.current_amount, remaining, right_agent.karma, left_agent.karma)
        assert right_decision in ["steal", "split"]        
        decisions = np.array([left_decision, right_decision])
        print(f"Agent {left_agent.name}={left_decision}"
              f" vs Agent {right_agent.name}={right_decision}")
            
        if all(decisions == "steal"):
            left_reward = 0
            right_reward = 0
        elif all(decisions == "split"):
            left_reward = self.current_amount / 2
            right_reward = self.current_amount / 2            
        elif left_decision == 'steal':
            left_reward = self.current_amount   
            right_reward = 0   
        elif right_decision == 'steal':
            right_reward = self.current_amount 
            left_reward = 0;
            
        print(f"Agent {left_agent.name} won {left_reward:.2f}"
              f" vs Agent {right_agent.name} won {right_reward:.2f}")            
            
        left_agent.total_amount += left_reward
        right_agent.total_amount += right_reward
        
        left_agent.result(
            left_decision, 
            right_decision, 
            self.current_amount, 
            left_reward)
            
        right_agent.result(
            right_decision, 
            left_decision, 
            self.current_amount, 
            right_reward)  

        if left_decision == "steal":
          left_agent.add_karma(-1)
        else:
          left_agent.add_karma(+1)
          
        if right_decision == "steal":
          right_agent.add_karma(-1)
        else:
          right_agent.add_karma(+1)            
                      

    def preround_render(self):
        # Render agent's name and stats
        rounds_text = font.render(f"Rounds played: {self.rounds_played}/{self.total_rounds}", True, BLACK)   
        screen.blit(rounds_text, (320, 50))   
        
        font_size = 72
        myfont = pygame.font.Font(None, font_size)        
        amount_text = myfont.render(f"$ {self.current_amount:.2f}", True, BLACK)   
        screen.blit(amount_text, (350, 200))    
                 
        
    def render(self):
        # Render agent's name and stats
        rounds_text = font.render(f"Rounds played: {self.rounds_played}/{self.total_rounds}", True, BLACK)   
        screen.blit(rounds_text, (320, 50))         

class Player:
    def __init__(self, agent):
        self.name = agent.get_name()
        self.agent = agent
        self.total_amount = 0
        self.last_decision = "none"
        self.karma = 0
        
    def reset_karma(self):
      self.karma = 0
          
    def add_karma(self, value):
      self.karma = min(max(self.karma + value, -5), 5)

    def render(self, x, y):
        # Draw background rectangle
        pygame.draw.rect(screen, BLACK, (x, y, 200, 80))

        # Draw agent's name and stats
        name_text = font.render(self.name, True, WHITE)        
        screen.blit(name_text, (x + 10, y + 10))
        amount_text = font.render(f"Amount: {self.total_amount:.2f}", True, WHITE)        
        screen.blit(amount_text, (x + 10, y + 30))

        if self.last_decision == "split":
            screen.blit(split_img, (x + 150, y + 10))
        elif self.last_decision == "steal":
            screen.blit(steal_img, (x + 150, y + 10))

    
    def preround_render(self, x, y):
        # Draw agent's name and stats
        pygame.draw.rect(screen, BLACK, (x, y, 200, 80))        
        karma_text = font.render(f"Karma: {self.karma}", True, WHITE)        
        screen.blit(karma_text, (x + 10, y + 50))
        
        name_text = font.render(self.name, True, WHITE)        
        screen.blit(name_text, (x + 10, y + 10))  
              
        amount_text = font.render(f"Amount: {self.total_amount:.2f}", True, WHITE)        
        screen.blit(amount_text, (x + 10, y + 30))    
        screen.blit(doubt_img, (x + 150, y + 10))
        
    def render(self, x, y):
        # Draw background rectangle
        pygame.draw.rect(screen, BLACK, (x, y, 200, 80))

        karma_text = font.render(f"Karma: {self.karma}", True, WHITE)        
        screen.blit(karma_text, (x + 10, y + 50))

        # Draw agent's name and stats
        name_text = font.render(self.name, True, WHITE)        
        screen.blit(name_text, (x + 10, y + 10))
        amount_text = font.render(f"Amount: {self.total_amount:.2f}", True, WHITE)        
        screen.blit(amount_text, (x + 10, y + 30))


        # Draw decision image
        if self.last_decision == "split":
            screen.blit(split_img, (x + 150, y + 10))
        elif self.last_decision == "steal":
            screen.blit(steal_img, (x + 150, y + 10))


    def decision(self, total_amount, rounds_played, your_karma, his_karma):
      self.last_decision = self.agent.decision(total_amount, rounds_played, your_karma, his_karma)
      return self.last_decision
      
    def result(self,  your_action, his_action, total_possible, reward):
      self.agent.result(your_action, his_action, total_possible, reward)


def play_round(game, agent1, agent2, remaining):
  print(f"{agent1.name} vs {agent2.name}")
  # Clear the screen
  screen.fill(BLACK)
  screen.blit(background_image, (0, 0))
  game.prepare_round()
  game.preround_render();
  agent1.preround_render(50, 50)
  agent2.preround_render(550, 50)        

  # Update the screen
  pygame.display.flip()
  for _ in range(4): 
    pygame.time.wait(1)    
  

  # Handle events
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit()
          exit()

  # Play a round
  game.play_round(agent1, agent2, remaining)

  # Render agents    
  screen.fill(BLACK) 
  screen.blit(background_image, (0, 0))    
  agent1.render(50, 50)
  agent2.render(550, 50)
  game.render();

 # Update the screen
  pygame.display.flip()
  for _ in range(4): 
    pygame.time.wait(100)  
    # pygame.time.wait(1)  # Para executar rápido


# Create two agents
agent1 = Player(simple_opponents.Splitter())
agent2 = Player(simple_opponents.Stealer())
agent3 = Player(simple_opponents.Randy())
agent4 = Player(simple_opponents.Karmine())
agent5 = Player(simple_opponents.Opportunist())
agent6 = Player(simple_opponents.Pretender())
agent_tittat = Player(your_agent.ReinforcementLearningAgent())

# Allgame
#agents = [agent1, agent2, agent3, agent4, agent5, agent6, ]

# Simple
agents = [Player(simple_opponents.Karmine()),  Player(simple_opponents.Karmine()), Player(rl_agent.RLAgent()), agent_tittat]

# Difficult 
# agents = [Player(your_agent.ReinforcementLearningAgent()), Player(your_agent.ReinforcementLearningAgent()), Player(rl_agent.RLAgent()), Player(your_agent.ReinforcementLearningAgent())]

# Very difficult
# agents = [Player(simple_opponents.Pretender()), Player(simple_opponents.Pretender()), Player(rl_agent.RLAgent()), Player(simple_opponents.Karmine())]

# Karma-aware
#agents = [Player(simple_opponents.Karmine()), Player(simple_opponents.Karmine()), Player(rl_agent.RLAgent()), Player(simple_opponents.Stealer())]

# Opportunists
# agents = [Player(simple_opponents.Opportunist()),Player(simple_opponents.Opportunist()), Player(rl_agent.RLAgent()), agent_tittat]

# 3 Karmines
# agents = [Player(simple_opponents.Karmine()),  Player(simple_opponents.Karmine()), Player(rl_agent.RLAgent()), Player(simple_opponents.Karmine())]

nrematches = 10 # Pode variar
nfullrounds = 100 # Número de ciclos completos
total_rounds = int(len(agents)*(len(agents) - 1) * nfullrounds * nrematches / 2)
game = Game(total_rounds)

from collections import defaultdict
matches_played = defaultdict(lambda: 0)
# Play rounds
while not game.isOver():
  random.shuffle(agents)
  for a in agents:
    a.reset_karma()
  
  for player1, player2 in combinations(agents, 2):
    matches_played[player1.name] += 1
    matches_played[player2.name] += 1
    print("==========")
    for remaining in reversed(range(0, nrematches)): 
      play_round(game, player1, player2, remaining)

print(matches_played)
max_score = -1
best = None
scores = []
for a in agents:
  print(f"O agente '{a.name}' obteve {a.total_amount:.2f}")
  if a.total_amount > max_score:
    best = a
    max_score = a.total_amount
print(f"Vencedor: {best.name}")
print(f"Score: {max_score:.2f}")

