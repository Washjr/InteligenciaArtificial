import random
import argparse
from maze import Maze
from search import AStarSearch
from world import World
from player import AdaptivePlayer, DefaultPlayer, RechargerPlayer  # importe aqui os players que desejar

def inicializar_game(seed, player_class, search_strategy_class, render):
    world = World(seed=seed, render=render, player_class=player_class)
    search_strategy = search_strategy_class(world)
    maze = Maze(world, render=render, search_strategy=search_strategy)
    return maze

def rodar_simulacao(seed, player_class, search_strategy_class):
    maze = inicializar_game(seed, player_class, search_strategy_class, render=False)
    resultado = maze.game_loop()
    resultado["seed"] = seed
    return resultado

def simulacao_monte_carlo(n_simulacoes=100, player_class=None, search_strategy=None):
    resultados = []
    for _ in range(n_simulacoes):
        seed = random.randint(0, 100000)
        resultado = rodar_simulacao(seed, player_class, search_strategy)
        resultados.append(resultado)
    return resultados

def analisar_resultados(resultados):
    n_simulacoes = len(resultados)

    media_passos = sum(r["passos"] for r in resultados) / n_simulacoes
    media_score = sum(r["score"] for r in resultados) / n_simulacoes
    media_entregas = sum(r["entregas"] for r in resultados) / n_simulacoes
    media_bateria = sum(r["bateria"] for r in resultados) / n_simulacoes
    scores_negativos = sum(1 for r in resultados if r["score"] < 0)

    print(f"Em {n_simulacoes} simulações:")

    print(f" • Média de passos: {media_passos:.2f}")
    print(f" • Média de score:      {media_score:.2f}")
    print(f" • Média de entregas: {media_entregas:.2f}")
    print(f" • Média de bateria:    {media_bateria:.2f}")
    print(f" • Percentual de scores negativos: {scores_negativos / n_simulacoes * 100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delivery Bot: Navegue no grid, colete pacotes e realize entregas."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Valor do seed para recriar o mesmo mundo (opcional).",
    )
    parser.add_argument(
        "--player",
        type=str,
        default="adaptive",
        help="Classe do player: adaptive ou default",
    )
    args = parser.parse_args()

    # maze = inicializar_game(args.seed, RechargerPlayer, AStarSearch, render=True)
    # maze.game_loop()

    resultados = simulacao_monte_carlo(n_simulacoes=1000, player_class=RechargerPlayer, search_strategy=AStarSearch)
    analisar_resultados(resultados)
