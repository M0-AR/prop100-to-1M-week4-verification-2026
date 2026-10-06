"""Capture docs/screenshots/preview.png from preview.html via headless browser.

Prefers Playwright (pip install playwright + playwright install chromium);
falls back to a matplotlib placeholder so the pipeline never breaks.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots" / "preview.png"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main():
    html = ROOT / "preview.html"
    url = html.as_uri()
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1440, "height": 2400})
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(OUT), full_page=True)
            b.close()
        print("captured", OUT)
    except Exception as e:
        print("playwright capture failed, writing placeholder:", e)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "preview.html placeholder\n(run: pip install playwright && playwright install chromium)",
                ha="center", va="center", fontsize=14)
        ax.axis("off")
        fig.savefig(OUT, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print("wrote placeholder", OUT)


if __name__ == "__main__":
    main()
