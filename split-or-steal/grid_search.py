import argparse
import random
import csv
from itertools import combinations
from collections import defaultdict

from game import Game
from player import Player
from agents.static_agents import Karmine, Randy, TitForTat
from agents.rl_agent import RLAgent

# Hyperparameter grid
grid = {
    'alpha': [0.1, 0.3, 0.5, 0.7, 0.9],
    'gamma': [0.5, 0.7, 0.9, 0.99],
    'epsilon': [0.01, 0.05, 0.1, 0.2]
}

# Tournament settings
MODE = 'simple'
n_rematches = 10
n_full_rounds = 100
repetitions = 3  # repete cada combinação para robustez

results = []

# Gera todas as combinações
defs = [(a, g, e) for a in grid['alpha'] for g in grid['gamma'] for e in grid['epsilon']]

for alpha, gamma, epsilon in defs:
    avg_score = 0.0
    for rep in range(repetitions):
        # Cria players: 2 x TitForTat + RLAgent(custom) + Karmine
        players = [Player(TitForTat()), Player(TitForTat()), Player(RLAgent(alpha, gamma, epsilon)), Player(Karmine())]

        total_rounds = int(len(players)*(len(players)-1)*n_full_rounds*n_rematches/2)
        game = Game(total_rounds, render=False)        
        matches_played = defaultdict(int)

        while not game.is_over():
            random.shuffle(players)

            for p in players: p.reset_karma()

            for p1, p2 in combinations(players, 2):
                for rem in reversed(range(n_rematches)):
                    game.prepare_round()
                    game.play_round(p1, p2, rem)

        # após torneio, acha RLAgent
        rl_player = next(p for p in players if isinstance(p.agent, RLAgent))
        avg_score += rl_player.total_amount
        
    avg_score /= repetitions
    results.append({'alpha': alpha, 'gamma': gamma, 'epsilon': epsilon, 'avg_score': avg_score})

# Escreve CSV
default_file = 'grid_search_results.csv'
with open(default_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['alpha','gamma','epsilon','avg_score'])
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"Grid search completo. Resultados em {default_file}")