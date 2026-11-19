
import requests
import socket
import ipaddress
import time

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from collections import deque


USER_AGENT = "WebMiningStudentBot/1.0"


def get_domain(url):
    """Mengambil nama domain dari URL."""
    hostname = urlparse(url).hostname

    if not hostname:
        return None

    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    return hostname


def normalize_url(url):
    """Memvalidasi dan membersihkan URL."""
    try:
        url, _ = urldefrag(url)
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return None

        if not parsed.hostname:
            return None

        if parsed.username or parsed.password:
            return None

        if parsed.port not in (None, 80, 443):
            return None

        return parsed._replace(
            fragment=""
        ).geturl().rstrip("/")

    except ValueError:
        return None


def is_public_url(url):
    """Mencegah akses ke alamat IP privat atau lokal."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False

        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM
        )

        if not addresses:
            return False

        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])

            if not ip.is_global:
                return False

        return True

    except (ValueError, socket.gaierror, OSError):
        return False


def can_crawl(url, session, robots_cache):
    """Memeriksa izin crawling berdasarkan robots.txt."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    if origin not in robots_cache:
        robots_url = origin + "/robots.txt"

        try:
            response = session.get(
                robots_url,
                timeout=10,
                allow_redirects=False
            )

            if response.status_code == 200:
                parser = RobotFileParser()
                parser.set_url(robots_url)
                parser.parse(response.text.splitlines())
                robots_cache[origin] = parser

            elif response.status_code == 404:
                robots_cache[origin] = None

            else:
                # Jika aturan tidak dapat diperiksa,
                # crawler tidak mengunjungi website.
                robots_cache[origin] = False

        except requests.RequestException:
            robots_cache[origin] = False

    rules = robots_cache[origin]

    if rules is False:
        return False

    if rules is None:
        return True

    return rules.can_fetch(USER_AGENT, url)


def fetch_page(url, session, robots_cache):
    """Mengambil halaman dengan pemeriksaan redirect."""

    current_url = url

    for _ in range(5):

        current_url = normalize_url(current_url)

        if not current_url or not is_public_url(current_url):
            return None, None

        if not can_crawl(
            current_url,
            session,
            robots_cache
        ):
            return None, None

        try:
            response = session.get(
                current_url,
                timeout=10,
                allow_redirects=False
            )

            # Menangani redirect secara manual
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")

                if not location:
                    return None, None

                current_url = urljoin(current_url, location)
                continue

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type", ""
            )

            if "text/html" not in content_type.lower():
                return None, None

            return response.text, current_url

        except requests.RequestException:
            return None, None

    return None, None


def crawl_web(start_url, max_depth=2, max_pages=30):
    """Melakukan crawling antarwebsite."""

    start_url = normalize_url(start_url)

    if not start_url or not is_public_url(start_url):
        raise ValueError("URL tidak valid atau bukan alamat publik.")

    visited = set()
    scheduled = {start_url}

    graph_edges = set()
    results = []

    queue = deque([(start_url, 0)])

    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT
    })

    robots_cache = {}

    while queue and len(visited) < max_pages:

        current_url, depth = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        html, final_url = fetch_page(
            current_url,
            session,
            robots_cache
        )

        if not html:
            continue

        source_domain = get_domain(final_url)

        results.append({
            "url": final_url,
            "domain": source_domain,
            "depth": depth
        })

        print(f"[CRAWLED] {final_url}")

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        if depth < max_depth:

            for link in soup.find_all("a", href=True):

                target_url = urljoin(
                    final_url,
                    link["href"]
                )

                target_url = normalize_url(target_url)

                if not target_url:
                    continue

                target_domain = get_domain(target_url)

                if not target_domain:
                    continue

                # Mencatat hubungan antar-domain
                if target_domain != source_domain:
                    graph_edges.add((
                        source_domain,
                        target_domain
                    ))

                    if (
                        target_url not in scheduled
                        and target_url not in visited
                        and len(scheduled) < max_pages
                    ):
                        queue.append((
                            target_url,
                            depth + 1
                        ))

                        scheduled.add(target_url)

        time.sleep(1)

    session.close()

    return results, sorted(graph_edges)
