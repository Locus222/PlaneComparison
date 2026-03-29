"""
conftest.py – sdílené fixtures pro Playwright testy PlaneComparison.

Flask server se spouští jednou pro celou testovací session ve vlákně na pozadí.
Každý test dostane čerstvou stránku prohlížeče a URL serveru přes fixture `app_url`.
"""
import threading
import time
import socket
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_PORT = 5099


def _port_open(port: int) -> bool:
    """Vrátí True, pokud je port již obsazen (server běží)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0


def _kill_port(port: int) -> None:
    """Ukončí proces držící daný port (Windows i Unix)."""
    import subprocess, platform
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if f":{port} " in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
    except Exception:
        pass


# ── Flask server fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app_url():
    """
    Spustí Flask server v daemon vlákně a vrátí base URL.
    Před startem ukončí případný starý proces na TEST_PORT.
    """
    import app as flask_app

    flask_app.app.config["TESTING"] = True

    # Vždy ukončíme starý proces a spustíme čerstvý server s aktuálním kódem
    if _port_open(TEST_PORT):
        _kill_port(TEST_PORT)
        time.sleep(0.8)

    def run():
        import logging
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        flask_app.app.run(port=TEST_PORT, use_reloader=False, threaded=True)

    t = threading.Thread(target=run, daemon=True)
    t.start()

    # Čekáme až 10 s, než server začne odpovídat
    for _ in range(40):
        if _port_open(TEST_PORT):
            break
        time.sleep(0.25)
    else:
        raise RuntimeError(f"Flask test server se nespustil na portu {TEST_PORT}")

    yield f"http://127.0.0.1:{TEST_PORT}"


# ── Playwright page fixture s auto-navigací ────────────────────────────────────

@pytest.fixture
def page(page, app_url):
    """
    Rozšíří výchozí Playwright `page` fixture o automatické přejití
    na hlavní stránku aplikace a počkání, až se načte tabulka.
    """
    page.goto(app_url, wait_until="domcontentloaded")
    # Čekáme, až proběhne úvodní auto-výpočet.
    # Signál: status-bar přestane říkat "Počítám…" (délka > 30 = výsledek nebo chyba)
    page.wait_for_function(
        "() => document.getElementById('status-bar').textContent.length > 30",
        timeout=20_000,
    )
    return page
