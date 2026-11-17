"""Browser regression: languages, actual light/dark contrast and passage search.

Uses a disposable headless Chrome profile, never the user's browser profile.
"""
import json
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def luminance(color):
    channels = [float(x) / 255 for x in color.removeprefix("rgb(").removesuffix(")").split(",")]
    linear = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in channels]
    return sum(x * weight for x, weight in zip(linear, [.2126, .7152, .0722]))


def check_contrast(page):
    colors = page.get_by_test_id("stMetric").first.evaluate("""element => {
        const app = document.querySelector('[data-testid="stApp"]');
        const style = getComputedStyle(element), appStyle = getComputedStyle(app);
        return {background: style.backgroundColor, text: style.color,
                appBackground: appStyle.backgroundColor, appText: appStyle.color};
    }""")
    if colors["background"] == "rgba(0, 0, 0, 0)":
        colors["background"] = colors["appBackground"]
    for foreground, background in [(colors["text"], colors["background"]),
                                   (colors["appText"], colors["appBackground"])]:
        assert background.startswith("rgb("), colors
        a, b = sorted([luminance(foreground), luminance(background)])
        assert (b + .05) / (a + .05) >= 4.5, colors
    return colors


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8050"
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(url)
        expect(page.get_by_role("textbox", name="Your question", exact=True)).to_be_visible()
        results = {}
        for theme in ["Light", "Dark"]:
            if not page.get_by_role("menuitemradio", name=theme, exact=True).is_visible():
                page.get_by_test_id("stMainMenu").click()
            page.get_by_role("menuitemradio", name=theme, exact=True).click()
            page.keyboard.press("Escape")
            # Theme selection updates client state asynchronously.
            page.wait_for_function(r"""expected => {
                const bg = getComputedStyle(document.querySelector('[data-testid="stApp"]')).backgroundColor;
                const c = bg.match(/\d+/g).map(Number);
                return expected === 'Dark' ? c[0] < 100 : c[0] > 200;
            }""", arg=theme)
            results[theme] = check_contrast(page)
            page.screenshot(path=str(ROOT / f"tmp/ui-en-{theme.lower()}.png"), full_page=True)
        # Switch languages through the actual selector.
        page.get_by_test_id("stSelectbox").first.get_by_role("combobox").click()
        page.get_by_role("option", name="中文", exact=True).click()
        expect(page.get_by_role("textbox", name="你的问题", exact=True)).to_be_visible()
        page.get_by_text("仅检索原文", exact=True).click()
        page.get_by_role("textbox", name="你的问题", exact=True).fill("LTCM 为什么会陷入流动性危机？")
        page.get_by_role("button", name="检索并回答", exact=True).click()
        expect(page.get_by_role("heading", name="原文依据", exact=True)).to_be_visible(timeout=60000)
        expect(page.get_by_test_id("stExpander").first).to_be_visible()
        page.get_by_test_id("stExpander").first.locator("summary").click()
        page.screenshot(path=str(ROOT / "tmp/ui-zh-dark-search.png"), full_page=True)
        assert check_contrast(page) == results["Dark"]
        # The English version uses the same retrieved evidence, without losing it.
        page.get_by_test_id("stSelectbox").first.get_by_role("combobox").click()
        page.get_by_role("option", name="English", exact=True).click()
        expect(page.get_by_role("heading", name="Source passages", exact=True)).to_be_visible()
        expect(page.get_by_role("textbox", name="Your question", exact=True)).to_have_value("LTCM 为什么会陷入流动性危机？")
        browser.close()
    print(json.dumps(results, indent=2))
    print("Browser light/dark contrast, language switch and passage search: PASS")


if __name__ == "__main__":
    main()
