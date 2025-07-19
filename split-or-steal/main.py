import argparse
import csv
import random
import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict

from game import Game
from player import Player
from agents.static_agents import (
   Karmine,
   Opportunist,
   Pretender,
   Randy,
   Splitter,
   Stealer,
   TitForTat,
   Pavlov, 
   ThresholdAgent
)
from agents.rl_agent import RLAgent
from agents.advanced_rl_agent import AdvancedRLAgent


def create_players(mode, rl_params=None) -> list[Player]:
    """Cria instâncias de Player de acordo com o modo escolhido."""
    def make_rl():
        return RLAgent(*rl_params) if rl_params else RLAgent()
    
    mapping = {
        'all':       [Splitter, Stealer, Randy, Karmine, Opportunist, Pretender, TitForTat, Pavlov, ThresholdAgent(), make_rl, AdvancedRLAgent],
        'simple':    [Karmine, Karmine, make_rl, TitForTat],
        'difficult': [TitForTat, TitForTat, make_rl, TitForTat],
        'very_difficult': [Pretender, Pretender, make_rl, Karmine],
        'karma_aware':    [Karmine, Karmine, make_rl, Stealer],
        'opportunists':   [Opportunist, Opportunist, make_rl, TitForTat],
        'three_karmines': [Karmine, Karmine, make_rl, Karmine],
        'pavlov_vs_tft':  [Pavlov, TitForTat, make_rl, Karmine],
        'threshold_mix':  [ThresholdAgent(25.0), ThresholdAgent(50.0), ThresholdAgent(75.0), make_rl],
    }
    if mode not in mapping:
        raise ValueError(f"Modo desconhecido: {mode}")
    raw = [cls() for cls in mapping[mode]]
    return [Player(agent) for agent in raw]


def run_single_tournament(render, mode, rl_params=None):
    """
    Executa um único torneio e retorna:
      scores: list of (agent_name, total_score)
      rl_rewards: list of rewards obtidos pelo RLAgent em cada rodada
    """
    # Agentes e modo de execução
    players = create_players(mode, rl_params)
    rl_player = next(p for p in players if isinstance(p.agent, RLAgent))
    rl_rewards = []

    # Cálculo de rounds
    n_rematches = 10
    n_full_rounds = 100
    total_rounds = int(len(players)*(len(players) - 1) * n_full_rounds * n_rematches / 2)
    game = Game(total_rounds, render=render)

    # Renomear duplicatas
    name_counts = defaultdict(int)
    for p in players:
        name_counts[p.name] += 1
        if name_counts[p.name] > 1:
            p.name = f"{p.name}#{name_counts[p.name]}"

    # Loop principal
    while not game.is_over():
        random.shuffle(players)
        for p in players:
            p.reset_karma()

        for p1, p2 in combinations(players, 2):
            is_rl_left  = (p1 is rl_player)
            is_rl_right = (p2 is rl_player)

            for rem in range(n_rematches - 1, -1, -1): 
                rl_reward = game.run_match(p1, p2, rem, is_rl_left, is_rl_right)
                if rl_reward is not None:
                    rl_rewards.append(rl_reward)

    # Resultados finais
    scores = [(p.name, p.total_amount) for p in players]
    return scores, rl_rewards


def run_montecarlo(render, mode, runs, rl_params=None):
    """
    Executa vários torneios e apresenta estatísticas agregadas.
    """
    all_scores = []
    for i in range(runs):
        print(f"Monte Carlo run {i+1}/{runs}")
        scores, _ = run_single_tournament(render, mode, rl_params)
        all_scores.append(scores)

    # Agrupa por agente
    agg = defaultdict(list)
    for scores in all_scores:
        for agent, val in scores:
            agg[agent].append(val)

    df = pd.DataFrame({
        'Agente': list(agg.keys()),
        'Média': [np.mean(v) for v in agg.values()],
        'Desvio padrão':  [np.std(v)  for v in agg.values()],
        '25%':  [np.percentile(v, 25) for v in agg.values()],
        '50%':  [np.percentile(v, 50) for v in agg.values()],
        '75%':  [np.percentile(v, 75) for v in agg.values()],
    })

    # Exibe tabela alinhada
    print('\n' + df.to_string(index=False, float_format='{:6.1f}'.format))


def main():
    parser = argparse.ArgumentParser(description='Torneio Split or Steal')
    parser.add_argument(
       '--render', 
       action='store_true', 
       help='Ativa renderização Pygame'
    )
    parser.add_argument(
        '--mode', 
        choices=[
            'all', 'simple', 'difficult', 'very_difficult',
            'karma_aware', 'opportunists', 'three_karmines',
            'pavlov_vs_tft', 'threshold_mix',
        ], 
        default='simple',
        help='Modo de dificuldade do torneio'
    )
    parser.add_argument(
        '--montecarlo', 
        type=int, 
        default=1,
        help='Número de réplicas para simulação Monte Carlo'
    )
    # Parâmetros RL customizados
    parser.add_argument('--alpha', type=float, default=0.5, help='Learning rate')
    parser.add_argument('--gamma', type=float, default=0.9, help='Discount factor')
    parser.add_argument('--epsilon', type=float, default=0.1, help='Exploration rate')

    args = parser.parse_args()

    rl_params = (args.alpha, args.gamma, args.epsilon)

    if args.montecarlo > 1:
        run_montecarlo(args.render, args.mode, args.montecarlo, rl_params)
    else:
        scores, _ = run_single_tournament(args.render, args.mode, rl_params)

        # Exibir resultados finais
        print("\nFim do torneio!\n")
        for agent, val in scores:
            print(f"Agente '{agent}' obteve {val:.2f}")

        winner = max(scores, key=lambda x: x[1])
        print(f"\nVencedor: {winner[0]} com {winner[1]:.2f}")

    
if __name__ == '__main__':
    main()