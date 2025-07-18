import argparse
import random
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
   TitForTat
)
from agents.rl_agent import RLAgent
from agents.advanced_rl_agent import AdvancedRLAgent


def create_players(mode) -> list[Player]:
    """Cria instâncias de Player de acordo com o modo escolhido."""
    if mode == 'all':
        raw = [Splitter(), Stealer(), Randy(), Karmine(), Opportunist(), Pretender(), TitForTat(), RLAgent(), AdvancedRLAgent()]
    elif mode == 'simple':
        raw = [Karmine(), Karmine(), RLAgent(), TitForTat()]
    elif mode == 'difficult':
        raw = [TitForTat(), TitForTat(), RLAgent(), TitForTat()]
    elif mode == 'very_difficult':
        raw = [Pretender(), Pretender(), RLAgent(), Karmine()]
    elif mode == 'karma_aware':
        raw = [Karmine(), Karmine(), RLAgent(), Stealer()]
    elif mode == 'opportunists':
        raw = [Opportunist(), Opportunist(), RLAgent(), TitForTat()]
    elif mode == 'three_karmines':
        raw = [Karmine(), Karmine(), RLAgent(), Karmine()]
    else:
        raise ValueError(f"Modo desconhecido: {mode}")
    return [Player(agent) for agent in raw]


def run_tournament(render, mode):
    # Players
    players = create_players(mode)

    n_rematches = 10
    n_full_rounds = 100
    total_rounds = int(len(players)*(len(players) - 1) * n_full_rounds * n_rematches / 2)

    game = Game(total_rounds, render=render)
    matches_played = defaultdict(lambda: 0)

    while not game.is_over():
        random.shuffle(players)

        for p in players:
            p.reset_karma()

        for p1, p2 in combinations(players, 2):
            matches_played[p1.name] += 1
            matches_played[p2.name] += 1

            print("==========")

            for rem in range(n_rematches - 1, -1, -1): 
                print(f"{p1.name} vs {p2.name}")
                game.prepare_round()
                
                if render:
                    game.render_start()
                    game.draw_player_preround(p1, x=50, y=50)
                    game.draw_player_preround(p2, x=550, y=50)
                    game.update_display()

                    game.handle_events()
                
                game.play_round(p1, p2, rem)

                if render:
                    game.render_end()
                    game.draw_player_postround(p1, x=50, y=50)
                    game.draw_player_postround(p2, x=550, y=50)
                    game.update_display()

    # Exibir resultados finais
    print("\nFim do torneio!\n")

    for p in players:
        print(f"Agente '{p.name}' obteve {p.total_amount:.2f}")

    winner = max(players, key=lambda p: p.total_amount)
    print(f"\nVencedor: {winner.name} com {winner.total_amount:.2f}")


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
            'karma_aware', 'opportunists', 'three_karmines'
        ], 
        default='simple',
        help='Modo de dificuldade do torneio'
    )
    args = parser.parse_args()
    run_tournament(render=args.render, mode=args.mode)


if __name__ == '__main__':
    main()