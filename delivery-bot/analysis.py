import random
import pandas as pd
import matplotlib.pyplot as plt

from main import rodar_simulacao
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

SEARCH_ALGORITHMS = [    
    GreedySearch,
    DijkstraSearch,
    AStarSearch,
    WeightedAStarSearch,
]

PLAYERS = [
    DefaultPlayer,      
    DoubleBatchPlayer,  
    FullBatchPlayer,
    AdaptivePlayer,
    ClusterAdaptivePlayer,
    RechargerPlayer,
    OptimalPlayer,
    OptimalRechargerPlayer,
]

def monte_carlo(player_cls, search_cls, seeds):
    """
    Executa n simulações Monte Carlo para um par (player, search).
    Retorna uma lista de dicionários com os resultados.
    """
    results = []
    for seed in seeds:        
        r = rodar_simulacao(seed, player_cls, search_cls)
        r["player"] = player_cls.__name__
        r["search"] = search_cls.__name__
        r["seed"] = seed
        results.append(r)
    return results

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por (player, search) e calcula estatísticas:
    passos, score, entregas, bateria, percentuais, tempo em ms.
    """
    summary = (
        df.groupby(["player","search"])
        .agg(
            mean_steps      = ("passos",  "mean"),
            std_steps       = ("passos",  "std"),
            mean_score      = ("score",   "mean"),
            std_score       = ("score",   "std"),
            mean_deliveries = ("entregas","mean"),
            std_deliveries  = ("entregas","std"),
            mean_battery    = ("bateria", "mean"),
            std_battery     = ("bateria", "std"),
            pct_score_neg   = ("score",   lambda s: (s < 0).mean() * 100),
            pct_batt_neg    = ("negative_battery_count", lambda s: (s > 0).mean() * 100),
            mean_search_ms  = ("avg_search_time", lambda s: s.mean() * 1000),
            std_search_ms   = ("avg_search_time", lambda s: s.std() * 1000),
            mean_time_ms    = ("sim_time", lambda s: s.mean() * 1000),
            std_time_ms     = ("sim_time", lambda s: s.std() * 1000),
        )
        .round(2)
        .reset_index()
    )
    return summary

def plot_metric(df: pd.DataFrame, metric: str, title: str, ylabel: str):
    """
    Plota um barplot comparativo do metric para cada player,
    com barras coloridas por estratégia de busca.
    """
    pivot = df.pivot(index="player", columns="search", values=metric)
    pivot.plot(kind="bar", figsize=(8,4))
    plt.title(title)
    plt.xlabel("Player")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.legend(title="Busca")
    plt.tight_layout()
    plt.show()

def plot_all(summary: pd.DataFrame):
    """
    Gera um gráfico para cada métrica de interesse.
    """
    plot_metric(summary, "mean_steps",       "Passos Médios",                  "Passos Médios")
    plot_metric(summary, "mean_score",       "Score Médio",                    "Pontos Médios")
    plot_metric(summary, "mean_deliveries",  "Entregas Médias",                "Entregas Médias")
    plot_metric(summary, "mean_battery",     "Bateria Média",                  "Carga Média Restante")
    plot_metric(summary, "pct_score_neg",    "% Scores Negativos",             "% Simulações Score < 0")
    plot_metric(summary, "pct_batt_neg",     "% Baterias Negativas",           "% Simulações Bateria Negativa")
    plot_metric(summary, "mean_search_ms",   "Tempo Médio por Busca (ms)",     "ms por Busca")
    plot_metric(summary, "mean_time_ms",     "Tempo Médio por Simulação (ms)", "ms por Simulação")

def main():   
    # 1) Gera um conjunto fixo de seeds
    num_simulations = 300
    random.seed(42)  # para reprodutibilidade
    seeds = [random.randint(0, 100_000) for _ in range(num_simulations)]

    # 2) Executa Monte Carlo com as mesmas seeds para cada player
    all_results = []
    for player in PLAYERS:
        for search in SEARCH_ALGORITHMS:
            print(f"Executando Monte Carlo para {player.__name__} + {search.__name__}...")
            all_results.extend(monte_carlo(player, search, seeds))

    # 3) Cria DataFrame e sumariza
    df      = pd.DataFrame(all_results)
    summary = summarize(df)

    # 4) Exibe e salva
    print("\n=== Resumo Comparativo (player × busca) ===")
    print(summary)

    summary.to_csv("player_comparison_summary.csv")
    print("\nResumo salvo em player_comparison_summary.csv")

    # 5) Plota gráficos
    plot_all(summary)

    for search_name in [alg.__name__ for alg in SEARCH_ALGORITHMS]:
        players_sorted = sorted(df["player"].unique())
        df_search = df[df["search"] == search_name]
        plt.figure(figsize=(12, 6))
        plt.boxplot(
            [df_search[df_search["player"] == player]["score"] for player in players_sorted],
            labels=players_sorted
        )
        plt.title(f"Boxplot do Score por Player ({search_name})")
        plt.xlabel("Player")
        plt.ylabel("Score")
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()