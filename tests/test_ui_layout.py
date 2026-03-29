"""
test_ui_layout.py – testy rozložení a základních UI prvků.

Ověřuje, že:
- stránka má správný titulek
- existují tři záložky (Obecné, Plán, Obsazení)
- horní panel a dolní panel jsou přítomny
- tabulka je přítomna a má záhlaví skupin
- action-bar obsahuje tlačítka
"""


def test_page_title(page):
    assert "PlaneComparison" in page.title()


def test_three_tabs_present(page):
    tabs = page.locator(".tab-btn")
    assert tabs.count() == 3
    labels = [tabs.nth(i).inner_text() for i in range(3)]
    assert any("Obecné"   in l for l in labels)
    assert any("Plán"     in l for l in labels)
    assert any("Obsazení" in l for l in labels)


def test_top_and_bottom_panels_present(page):
    assert page.locator("#top-panel").is_visible()
    assert page.locator("#bottom-panel").is_visible()


def test_results_table_present(page):
    assert page.locator("#results-table").is_visible()


def test_table_group_headers(page):
    group_headers = page.locator("thead tr.group-row th")
    texts = [group_headers.nth(i).inner_text() for i in range(group_headers.count())]
    joined = " ".join(texts)
    assert "Identifikace"    in joined
    assert "Hmotnosti"       in joined
    assert "Max Power"       in joined
    assert "Economy Cruise"  in joined


def test_action_bar_buttons(page):
    assert page.locator("#btn-compute").is_visible()
    assert page.locator("#toggle-unsuitable").is_visible()


def test_status_bar_present(page):
    assert page.locator("#status-bar").is_visible()


def test_summary_bar_present(page):
    assert page.locator("#summary-bar").is_visible()

