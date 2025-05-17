import random
import pandas as pd
import matplotlib.pyplot as plt

from main import rodar_simulacao
from search import AStarSearch
from player import (
    DefaultPlayer, 
    AdaptivePlayer, 
    BatchCollectorPlayer, 
    RechargerPlayer, 
    OptimalPlayer
)

def monte_carlo(player_cls, seeds):
    """
    Executa n simulações Monte Carlo para a classe de player fornecida.
    Retorna uma lista de dicionários com os resultados.
    """
    results = []
    for seed in seeds:        
        r = rodar_simulacao(seed, player_cls, AStarSearch)
        r["player"] = player_cls.__name__
        r["seed"] = seed
        results.append(r)
    return results

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa por 'player' e calcula estatísticas descritivas e percentuais.
    """
    summary = df.groupby("player").agg(
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
        mean_time_s     = ("sim_time","mean"),
    )
    return summary

def plot_summary(summary: pd.DataFrame):
    """
    Plota gráficos de barras para as principais métricas do summary.
    """
    metrics = {
        "mean_steps":    ("Passos Médios",            "Número Médio de Passos"),
        "mean_score":    ("Score Médio",              "Pontos Médios"),
        "pct_score_neg": ("% de Scores Negativos",     "Percentual de Simulações com Score < 0"),
        "pct_batt_neg":  ("% de Baterias Negativas",   "Percentual de Simulações com Bateria Negativa"),
    }

    for metric, (title, ylabel) in metrics.items():
        plt.figure(figsize=(6,4))
        summary[metric].plot(kind="bar")
        plt.title(title)
        plt.xlabel("Player")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def main():
    players = [
        DefaultPlayer,
        AdaptivePlayer,
        BatchCollectorPlayer,
        RechargerPlayer,
        OptimalPlayer,
    ]

    # 1) Gera um conjunto fixo de seeds
    num_simulations = 300
    random.seed(42)  # para reprodutibilidade
    seeds = [random.randint(0, 100_000) for _ in range(num_simulations)]

    # 2) Executa Monte Carlo com as mesmas seeds para cada player
    all_results = []
    for cls in players:
        print(f"Executando Monte Carlo para {cls.__name__}...")
        all_results.extend(monte_carlo(cls, seeds))

    # 3) Cria DataFrame e sumariza
    df      = pd.DataFrame(all_results)
    summary = summarize(df).round(2)

    # 4) Exibe e salva
    print("\n=== Resumo Comparativo ===")
    print(summary)
    summary.to_csv("player_comparison_summary.csv")
    print("\nResumo salvo em player_comparison_summary.csv")

    # 5) Plota gráficos
    plot_summary(summary)

if __name__ == "__main__":
    main()