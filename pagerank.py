
import networkx as nx
import pandas as pd


def calculate_pagerank(edges, damping_factor=0.85):
    """
    Menghitung PageRank berdasarkan hubungan antarwebsite.
    """

    # Membuat directed graph
    graph = nx.DiGraph()

    # Memasukkan hubungan antarwebsite
    graph.add_edges_from(edges)

    # Memeriksa graph
    if graph.number_of_nodes() == 0:
        return graph, pd.DataFrame()

    # Menghitung PageRank
    pagerank_scores = nx.pagerank(
        graph,
        alpha=damping_factor,
        max_iter=100,
        tol=1e-6
    )

    # Mengubah hasil menjadi DataFrame
    results = pd.DataFrame(
        pagerank_scores.items(),
        columns=["Website", "PageRank"]
    )

    # Mengurutkan berdasarkan PageRank tertinggi
    results = results.sort_values(
        by="PageRank",
        ascending=False
    ).reset_index(drop=True)

    # Menambahkan peringkat
    results.index = results.index + 1
    results.index.name = "Peringkat"

    return graph, results
