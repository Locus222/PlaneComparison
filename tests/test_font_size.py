"""
test_font_size.py – Playwright testy pro pill slider velikosti písma.

Slider je umístěn na kartě Obecné.
Všechny texty aplikace dědí velikost z CSS proměnné --app-fs.
"""

FONT_SIZES = {"small": "13px", "medium": "15px", "large": "17px"}
# Labely odpovídají HTML: "Small – 13 pt" atd.
LABELS = ["Small – 13 pt", "Medium – 15 pt", "Large – 17 pt"]


def _get_app_fs(page) -> str:
    """Vrátí aktuální hodnotu CSS proměnné --app-fs."""
    return page.evaluate(
        "() => getComputedStyle(document.documentElement)"
        ".getPropertyValue('--app-fs').trim()"
    )


def _click_font(page, value: str):
    """Klikne na radio button font-size slideru přes JS a počká na aplikaci."""
    page.evaluate(f"() => document.getElementById('fs-{value}').click()")
    page.wait_for_timeout(100)


def _go_general(page):
    """Přepne na záložku Obecné."""
    page.locator(".tab-btn", has_text="Obecné").click()


# ── Přítomnost a struktura ─────────────────────────────────────────────────────

def test_font_slider_present(page):
    """Font-size slider je přítomen na kartě Obecné."""
    _go_general(page)
    assert page.locator("#font-slider").is_visible()


def test_font_slider_has_three_options(page):
    """Slider má tři labely s popisem velikosti."""
    _go_general(page)
    labels = page.locator("#font-slider label").all_inner_texts()
    assert labels == LABELS


def test_font_slider_in_general_tab(page):
    """Slider je součástí karty Obecné (ne action-baru)."""
    assert page.locator("#tab-general #font-slider").count() == 1
    assert page.locator("#action-bar #font-slider").count() == 0


# ── Výchozí stav ───────────────────────────────────────────────────────────────

def test_default_font_size_is_small(page):
    """Výchozí aktivní možnost je Small."""
    checked = page.evaluate(
        "() => document.querySelector('input[name=\"fontsize\"]:checked').value"
    )
    assert checked == "small"


def test_default_app_fs_is_13px(page):
    """Výchozí --app-fs je 13px."""
    assert _get_app_fs(page) == "13px"


# ── Přepínání velikostí ────────────────────────────────────────────────────────

def test_click_medium_sets_15px(page):
    """Kliknutí na Medium nastaví --app-fs na 15px (small + 2pt)."""
    _click_font(page, "medium")
    assert _get_app_fs(page) == "15px"


def test_click_large_sets_17px(page):
    """Kliknutí na Large nastaví --app-fs na 17px (small + 4pt)."""
    _click_font(page, "large")
    assert _get_app_fs(page) == "17px"


def test_click_small_restores_13px(page):
    """Návrat na Small obnoví --app-fs na 13px."""
    _click_font(page, "large")
    _click_font(page, "small")
    assert _get_app_fs(page) == "13px"


def test_cycle_s_m_l_s(page):
    """Cyklické přepínání Small→Medium→Large→Small dá vždy správnou hodnotu."""
    for val, expected in [("small", "13px"), ("medium", "15px"),
                          ("large", "17px"), ("small", "13px")]:
        _click_font(page, val)
        got = _get_app_fs(page)
        assert got == expected, f"Po kliknutí na {val!r}: očekáváno {expected}, dostáno {got}"


# ── Aplikace na všechny texty ──────────────────────────────────────────────────

def test_body_font_size_reflects_variable(page):
    """Skutečný computed font-size body odpovídá --app-fs."""
    for val, expected_px in [("small", "13px"), ("medium", "15px"), ("large", "17px")]:
        _click_font(page, val)
        body_fs = page.evaluate(
            "() => getComputedStyle(document.body).fontSize"
        )
        assert body_fs == expected_px, \
            f"{val}: body font-size={body_fs!r}, očekáváno {expected_px!r}"


def test_table_font_size_scales(page):
    """Font-size tabulky (v em) se skutečně zvětší po přepnutí na Large."""
    _click_font(page, "small")
    small_fs = page.evaluate(
        "() => parseFloat(getComputedStyle(document.querySelector('#results-table')).fontSize)"
    )
    _click_font(page, "large")
    large_fs = page.evaluate(
        "() => parseFloat(getComputedStyle(document.querySelector('#results-table')).fontSize)"
    )
    assert large_fs > small_fs, \
        f"Tabulka: large ({large_fs}px) by měla být větší než small ({small_fs}px)"


def test_tab_btn_font_size_scales(page):
    """Font-size záložek se zvětší po přepnutí na Large."""
    _click_font(page, "small")
    small_fs = page.evaluate(
        "() => parseFloat(getComputedStyle(document.querySelector('.tab-btn')).fontSize)"
    )
    _click_font(page, "large")
    large_fs = page.evaluate(
        "() => parseFloat(getComputedStyle(document.querySelector('.tab-btn')).fontSize)"
    )
    assert large_fs > small_fs


# ── Radio stav ─────────────────────────────────────────────────────────────────

def test_medium_radio_checked_after_click(page):
    """Po kliknutí na Medium je radio fs-medium checked."""
    _click_font(page, "medium")
    assert page.evaluate("() => document.getElementById('fs-medium').checked") is True


def test_only_one_radio_checked_at_a_time(page):
    """Vždy je checked právě jedno radio."""
    _click_font(page, "medium")
    count = page.evaluate(
        "() => document.querySelectorAll('input[name=\"fontsize\"]:checked').length"
    )
    assert count == 1


# ── Ostatní UI nenarušeno ──────────────────────────────────────────────────────

def test_table_still_visible_after_font_change(page):
    """Tabulka zůstane viditelná po změně velikosti písma."""
    _click_font(page, "large")
    assert page.locator("#results-table").is_visible()


def test_compute_still_works_after_font_change(page):
    """Výpočet stále funguje po změně velikosti písma."""
    _click_font(page, "large")
    page.evaluate("() => { document.getElementById('status-bar').textContent = ''; }")
    page.locator("#btn-compute").click()
    page.wait_for_function(
        "() => document.getElementById('status-bar').textContent.length > 30",
        timeout=10_000,
    )
    assert page.locator("#table-body tr:not(.unsuitable)").count() >= 1

