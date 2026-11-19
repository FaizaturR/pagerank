
import streamlit as st
import streamlit.components.v1 as components

from crawler import crawl_web
from pagerank import calculate_pagerank
from visualization import create_network_graph


# ==========================================
# KONFIGURASI HALAMAN
# ==========================================

st.set_page_config(
    page_title="Web Mining & PageRank",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Web Mining & PageRank")

st.write(
    "Aplikasi untuk melakukan web crawling, "
    "analisis PageRank, dan visualisasi hubungan antarwebsite."
)

st.divider()


# ==========================================
# PENGATURAN WEB CRAWLING
# ==========================================

st.subheader("Pengaturan Web Crawling")

url = st.text_input(
    "Masukkan URL website:",
    placeholder="https://www.python.org"
)

col1, col2 = st.columns(2)

with col1:
    max_depth = st.number_input(
        "Kedalaman Crawling",
        min_value=1,
        max_value=5,
        value=2
    )

with col2:
    max_pages = st.number_input(
        "Maksimal Halaman",
        min_value=1,
        max_value=100,
        value=30
    )


# ==========================================
# PROSES WEB CRAWLING
# ==========================================

if st.button("🚀 Mulai Crawling", type="primary"):

    if not url.strip():

        st.warning("Masukkan URL website terlebih dahulu.")

    else:

        try:

            with st.spinner("Sedang melakukan web crawling..."):

                # Tahap 1: Web Crawling
                results, edges = crawl_web(
                    url,
                    max_depth=int(max_depth),
                    max_pages=int(max_pages)
                )

            st.success("Web crawling selesai!")

            # ==================================
            # HASIL WEB CRAWLING
            # ==================================

            st.subheader("1. Hasil Web Crawling")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Jumlah Halaman",
                    len(results)
                )

            with col2:
                st.metric(
                    "Jumlah Hubungan",
                    len(edges)
                )

            if results:

                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True
                )

            # ==================================
            # HUBUNGAN ANTARWEBSITE
            # ==================================

            if edges:

                st.subheader("2. Hubungan Antarwebsite")

                edge_data = [
                    {
                        "Website Sumber": source,
                        "Website Tujuan": target
                    }
                    for source, target in edges
                ]

                st.dataframe(
                    edge_data,
                    use_container_width=True,
                    hide_index=True
                )

                # ==================================
                # ANALISIS PAGERANK
                # ==================================

                graph, pagerank_results = calculate_pagerank(edges)

                st.subheader("3. Hasil Analisis PageRank")

                if not pagerank_results.empty:

                    # Format angka PageRank menjadi 6 desimal
                    styled_results = pagerank_results.style.format({
                        "PageRank": "{:.6f}"
                    })

                    st.dataframe(
                        styled_results,
                        use_container_width=True
                    )

                    # ==================================
                    # VISUALISASI JARINGAN WEBSITE
                    # ==================================

                    st.subheader("4. Visualisasi Jaringan Website")

                    st.caption(
                        "Graf menunjukkan hubungan dan arah tautan "
                        "antarwebsite berdasarkan hasil crawling."
                    )

                

                    graph_html = create_network_graph(
                        graph,
                        pagerank_results
                    )

                    components.html(
                        graph_html,
                        height=700,
                        scrolling=True
                    )

                else:

                    st.info("Belum ada data PageRank.")

            else:

                st.warning(
                    "Tidak ditemukan hubungan antarwebsite "
                    "dari halaman yang berhasil di-crawl."
                )

        except Exception as e:

            st.error(f"Terjadi kesalahan: {e}")
