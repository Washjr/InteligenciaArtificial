import argparse
import random
import time

from maze import Maze
from world import World
from search import (
    GreedySearch, 
    DijkstraSearch, 
    AStarSearch, 
    WeightedAStarSearch
)
from player import (
    DefaultPlayer,
    DoubleBatchPlayer,     
    FullBatchPlayer, 
    AdaptivePlayer,
    ClusterAdaptivePlayer, 
    RechargerPlayer, 
    OptimalPlayer,
    OptimalRechargerPlayer
)

PLAYER_REGISTRY = {
    'default':  DefaultPlayer,
    'double':   DoubleBatchPlayer,
    'full':     FullBatchPlayer,
    'adaptive': AdaptivePlayer,
    'cluster':  ClusterAdaptivePlayer,
    'recharge': RechargerPlayer,
    'optimal':  OptimalPlayer,
    'opt-rech': OptimalRechargerPlayer,
}

SEARCH_REGISTRY = {
    'greedy':   GreedySearch,
    'dijkstra': DijkstraSearch,
    'astar':    AStarSearch,
    'wastar':   WeightedAStarSearch,
}

# render é um parâmetro que indica se o jogo deve ser renderizado ou não, util para simulações 
def inicializar_game(seed, player_class, search_strategy_class, render):
    world = World(seed=seed, render=render, player_class=player_class)
    search_strategy = search_strategy_class(world)
    maze = Maze(world, render=render, search_strategy=search_strategy)
    return maze

def rodar_simulacao(seed, player_class, search_strategy_class):
    start_sim = time.perf_counter()
    maze = inicializar_game(seed, player_class, search_strategy_class, render=False)
    resultado = maze.game_loop()
    end_sim = time.perf_counter()

    resultado["seed"] = seed
    resultado["sim_time"] = end_sim - start_sim    # tempo total em segundos
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
    baterias_negativas = sum(r["negative_battery_count"] for r in resultados)   
    media_tempo_busca = sum(r["avg_search_time"] for r in resultados) / n_simulacoes
    media_tempo_simulacao = sum(r["sim_time"] for r in resultados) / n_simulacoes 
    negative_seeds = [r["seed"] for r in resultados if r["score"] < 0]

    print(f"Em {n_simulacoes} simulações:")
    print(f" • Média de passos: {media_passos:.2f}")
    print(f" • Média de score: {media_score:.2f}")
    print(f" • Média de entregas: {media_entregas:.2f}")
    print(f" • Média de bateria: {media_bateria:.2f}")
    print(f" • Percentual de scores negativos: {scores_negativos / n_simulacoes * 100:.2f}%")
    print(f" • Percentual de baterias negativas: {baterias_negativas / n_simulacoes * 100:.2f}%")
    print(f" • Tempo médio de busca: {media_tempo_busca*1000:.2f} ms")
    print(f" • Tempo médio por simulação: {media_tempo_simulacao*1000:.2f} ms")

    if negative_seeds:
        print(f" • Seeds com score negativo ({len(negative_seeds)} casos):")
        print(f"   {negative_seeds}")
    else:
        print(" • Nenhum score negativo encontrado.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Delivery Bot: navegue no grid, colete pacotes e realize entregas. "
            "Escolha player, algoritmo de busca, modo de execução e número de runs (bench)."
        )
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
        default="opt-rech",
        choices=PLAYER_REGISTRY.keys(),
        help="Qual player usar (choices: %(choices)s)",
    )
    parser.add_argument(
        "--search",
        type=str,
        default="astar",
        choices=SEARCH_REGISTRY.keys(),
        help="Qual algoritmo de busca usar (choices: %(choices)s)",
    )
    parser.add_argument(
        "--mode",
        choices=["play", "bench"],
        default="play",
        help="play: executa com pygame  bench: roda Monte Carlo"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=300,
        help="Número de simulações a executar no modo 'bench'.",
    )
    args = parser.parse_args()

    player_cls = PLAYER_REGISTRY[args.player]
    search_cls = SEARCH_REGISTRY[args.search]

    # Mensagem de startup
    print(f"[START] Mode={args.mode} | Player={args.player} | Search={args.search} | Seed={args.seed}")

    try:
        if args.mode == "play":
            maze = inicializar_game(args.seed, player_cls, search_cls, render=True)
            maze.game_loop()
        else:
            print(f"Executando benchmark com {args.runs} simulações... ")
            resultados = simulacao_monte_carlo(
                n_simulacoes=args.runs,
                player_class=player_cls,
                search_strategy=search_cls
            )
            analisar_resultados(resultados)
    except KeyboardInterrupt:
        # Permite ao usuário sair limpo com Ctrl+C
        print("\n[INTERRUPTED] Simulação interrompida pelo usuário.")
    finally:
        print("[END] Execução finalizada.")