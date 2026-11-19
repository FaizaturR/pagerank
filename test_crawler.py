
import requests

from crawler import (
    normalize_url,
    is_public_url,
    can_crawl,
    fetch_page
)

url = "https://www.wikipedia.org"

session = requests.Session()
robots_cache = {}

print("===== DIAGNOSTIK WIKIPEDIA =====")

# 1. Pemeriksaan URL
normalized = normalize_url(url)
print("1. Normalisasi URL:", normalized)

# 2. Pemeriksaan alamat IP
print("2. URL publik:", is_public_url(normalized))

# 3. Pemeriksaan robots.txt
try:
    allowed = can_crawl(normalized, session, robots_cache)
    print("3. Diizinkan robots.txt:", allowed)
except Exception as e:
    print("3. Error robots.txt:", repr(e))

# 4. Pemeriksaan pengambilan halaman
try:
    html, final_url = fetch_page(
        normalized,
        session,
        robots_cache
    )

    print("4. URL akhir:", final_url)
    print("5. Panjang HTML:", len(html) if html else 0)

except Exception as e:
    print("4. Error mengambil halaman:", repr(e))
