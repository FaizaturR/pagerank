
from pyvis.network import Network


def create_network_graph(graph, pagerank_results):

    net = Network(
        height="650px",
        width="100%",
        directed=True,
        bgcolor="#F8FAFC",
        font_color="#1E293B",
        notebook=False
    )

    # Mengurutkan hasil PageRank
    scores = dict(
        zip(
            pagerank_results["Website"],
            pagerank_results["PageRank"]
        )
    )

    rankings = {
        website: rank
        for rank, website in enumerate(
            pagerank_results["Website"],
            start=1
        )
    }

    max_score = max(scores.values()) if scores else 1

    # Warna berdasarkan peringkat
    rank_colors = {
        1: "#F59E0B",  # Emas
        2: "#94A3B8",  # Perak
        3: "#CD7F32"   # Perunggu
    }

    # Menambahkan node website
    for website in graph.nodes():

        score = scores.get(website, 0)
        rank = rankings.get(website, 0)

        color = rank_colors.get(rank, "#3B82F6")

        size = 25 + (score / max_score * 30) if max_score else 25

        net.add_node(
            website,
            label=website,
            title=(
                f"<b>{website}</b><br>"
                f"Peringkat: {rank}<br>"
                f"PageRank: {score:.6f}"
            ),
            size=size,
            color={
                "background": color,
                "border": "#334155",
                "highlight": {
                    "background": "#38BDF8",
                    "border": "#0F172A"
                }
            },
            borderWidth=2,
            font={
                "size": 20,
                "face": "Arial",
                "color": "#1E293B",
                "bold": True
            }
        )

    # Menambahkan hubungan antarwebsite
    for source, target in graph.edges():

        net.add_edge(
            source,
            target,
            arrows={
                "to": {
                    "enabled": True,
                    "scaleFactor": 1.2
                }
            },
            color="#64748B",
            width=2,
            smooth={
                "type": "curvedCW",
                "roundness": 0.15
            }
        )

    # Pengaturan tampilan dan jarak node
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -30000,
                "centralGravity": 0.15,
                "springLength": 250,
                "springConstant": 0.04,
                "avoidOverlap": 1
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 200,
            "zoomView": true,
            "dragView": true,
            "dragNodes": true,
            "navigationButtons": true
        },
        "edges": {
            "font": {
                "size": 12
            }
        }
    }
    """)

    return net.generate_html()
