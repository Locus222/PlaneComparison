"""
test_currency.py – Playwright testy pro výběr měny (pill slider) na kartě Obecné.
"""

COMPUTED_JS = "() => document.getElementById('status-bar').textContent.length > 30"


def _wait_computed(page, timeout=10_000):
    page.wait_for_function(COMPUTED_JS, timeout=timeout)


def _click_and_wait(page, timeout=12_000):
    """Resetuje status-bar na prázdno, klikne Vypočítat, počká na dokončení."""
    page.evaluate("() => { document.getElementById('status-bar').textContent = ''; }")
    page.locator("#btn-compute").click()
    page.wait_for_function(COMPUTED_JS, timeout=timeout)


def _select_currency(page, value):
    """Vybere měnu kliknutím na radio input (přes JS) a počká na change event."""
    page.evaluate(
        "([v]) => { document.getElementById('cur-' + v.toLowerCase()).click(); }",
        [value]
    )
    page.wait_for_timeout(150)  # dáme čas change event listeneru


def _set_rate(page, field_id, value):
    """Nastaví kurz-pole přes DOM (obchází visibility check)."""
    page.evaluate(f"() => {{ document.getElementById('{field_id}').value = '{value}'; }}")


def _header_sym(page) -> str:
    return page.locator(".cost-sym").first.inner_text()


def _first_total_econ(page) -> str:
    return page.evaluate("""() => {
        const rows = [...document.querySelectorAll('#table-body tr:not(.unsuitable)')];
        if (!rows.length) return '';
        const tds = rows[0].querySelectorAll('td');
        return tds[27] ? tds[27].innerText : '';
    }""")


def _parse_cost(text: str) -> float:
    import re
    digits = re.sub(r"[^\d,]", "", text).replace(",", ".")
    parts = digits.split(".")
    if len(parts) > 2:
        digits = "".join(parts[:-1]) + "." + parts[-1]
    return float(digits) if digits else 0.0


# ── Přítomnost slideru ─────────────────────────────────────────────────────────

def test_slider_present(page):
    assert page.locator("#currency-slider").is_visible()


def test_slider_has_four_options(page):
    labels = page.locator("#currency-slider label").all_inner_texts()
    assert labels == ["CZK", "EUR", "USD", "GBP"]


def test_default_currency_czk(page):
    checked = page.evaluate(
        "() => document.querySelector('input[name=\"currency\"]:checked').value"
    )
    assert checked == "CZK"


def test_default_header_shows_kc(page):
    assert _header_sym(page) == "Kč"


# ── Skrytí/zobrazení kurz-polí ─────────────────────────────────────────────────

def test_rate_fields_hidden_by_default(page):
    assert not page.locator("#rate-eur").is_visible()
    assert not page.locator("#rate-usd").is_visible()
    assert not page.locator("#rate-gbp").is_visible()


def test_click_eur_shows_eur_rate_field(page):
    _select_currency(page, "EUR")
    assert page.locator("#rate-eur").is_visible()
    assert not page.locator("#rate-usd").is_visible()
    assert not page.locator("#rate-gbp").is_visible()


def test_click_usd_shows_usd_rate_field(page):
    _select_currency(page, "USD")
    assert page.locator("#rate-usd").is_visible()
    assert not page.locator("#rate-eur").is_visible()


def test_click_gbp_shows_gbp_rate_field(page):
    _select_currency(page, "GBP")
    assert page.locator("#rate-gbp").is_visible()
    assert not page.locator("#rate-eur").is_visible()


def test_back_to_czk_hides_all_rate_fields(page):
    _select_currency(page, "EUR")
    _select_currency(page, "CZK")
    assert not page.locator("#rate-eur").is_visible()
    assert not page.locator("#rate-usd").is_visible()
    assert not page.locator("#rate-gbp").is_visible()


# ── Výchozí hodnoty kurzů ──────────────────────────────────────────────────────

def test_default_eur_rate(page):
    """Výchozí hodnota 1 EUR = 24.545 CZK."""
    val = float(page.locator("#eur_to_czk").input_value())
    assert abs(val - 24.545) < 0.001


def test_default_usd_rate(page):
    """Výchozí hodnota 1 USD = 21.315 CZK."""
    val = float(page.locator("#usd_to_czk").input_value())
    assert abs(val - 21.315) < 0.001


def test_default_gbp_rate(page):
    """Výchozí hodnota 1 GBP = 28.299 CZK."""
    val = float(page.locator("#gbp_to_czk").input_value())
    assert abs(val - 28.299) < 0.001


# ── Záhlaví po výpočtu ─────────────────────────────────────────────────────────

def test_eur_header_after_compute(page):
    _select_currency(page, "EUR")
    _click_and_wait(page)
    assert _header_sym(page) == "€"


def test_usd_header_after_compute(page):
    _select_currency(page, "USD")
    _click_and_wait(page)
    assert _header_sym(page) == "$"


def test_gbp_header_after_compute(page):
    _select_currency(page, "GBP")
    _click_and_wait(page)
    assert _header_sym(page) == "£"


def test_czk_header_after_switching_back(page):
    _select_currency(page, "EUR")
    _click_and_wait(page)
    _select_currency(page, "CZK")
    _click_and_wait(page)
    assert _header_sym(page) == "Kč"


# ── Numerická správnost ────────────────────────────────────────────────────────

def test_eur_costs_numerically_lower_than_czk(page):
    """Náklady v EUR jsou numericky menší než v CZK."""
    _select_currency(page, "CZK")
    _click_and_wait(page)
    czk_text = _first_total_econ(page)

    _select_currency(page, "EUR")
    _set_rate(page, "eur_to_czk", "24.545")
    _click_and_wait(page)
    eur_text = _first_total_econ(page)

    czk_val = _parse_cost(czk_text)
    eur_val = _parse_cost(eur_text)
    assert czk_val > 0 and eur_val > 0, f"CZK={czk_text!r}, EUR={eur_text!r}"
    assert eur_val < czk_val


def test_lower_czk_per_eur_gives_higher_eur_cost(page):
    """Nižší kurz (1 EUR = 10 CZK) → vyšší EUR cena než při 1 EUR = 24.545 CZK."""
    _select_currency(page, "EUR")
    _set_rate(page, "eur_to_czk", "24.545")
    _click_and_wait(page)
    normal_val = _parse_cost(_first_total_econ(page))

    _set_rate(page, "eur_to_czk", "10.0")
    _click_and_wait(page)
    cheap_val = _parse_cost(_first_total_econ(page))

    assert normal_val > 0 and cheap_val > 0
    assert cheap_val > normal_val
