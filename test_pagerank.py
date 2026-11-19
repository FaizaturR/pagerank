
from pagerank import calculate_pagerank

# Data hubungan antarwebsite
edges = [
    ("iana.org", "icann.org"),
    ("iana.org", "pti.icann.org"),
]

# Menghitung PageRank
graph, results = calculate_pagerank(
    edges,
    damping_factor=0.85
)

print("===== GRAPH WEBSITE =====")
print("Jumlah Node:", graph.number_of_nodes())
print("Jumlah Edge:", graph.number_of_edges())

print("\n===== HASIL PAGERANK =====")
print(results)
