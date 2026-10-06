"""Generate results/equity.png + docs/demo.gif from REAL results (no hand edits)."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
DOCS = ROOT / "docs"


def main():
    eq = pd.read_csv(RES / "equity.csv")
    y = eq.iloc[:, 0].values
    # equity.png
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(y, linewidth=2)
    ax.axhline(10000, linestyle="--", linewidth=1)
    ax.axhline(10500, linestyle=":", linewidth=1)
    ax.set_title("Pooled equity — $10K start, 1.5%/trade, daily proxy (2020-2026)")
    ax.set_xlabel("trade index")
    ax.set_ylabel("equity ($)")
    fig.tight_layout()
    fig.savefig(RES / "equity.png", dpi=150)
    plt.close(fig)
    # demo.gif: progressive reveal of equity + watermark of key stats
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    line, = ax2.plot([], [], linewidth=2)
    ax2.set_xlim(0, max(1, len(y) - 1))
    ax2.set_ylim(min(y.min(), 10000) * 0.999, max(y.max(), 10500) * 1.001)
    ax2.axhline(10000, linestyle="--", linewidth=1)
    ax2.set_title("Demo: equity builds trade by trade (40 trades)")
    ax2.set_xlabel("trade #")
    ax2.set_ylabel("$")

    def upd(i):
        line.set_data(range(i + 1), y[: i + 1])
        return (line,)

    ani = animation.FuncAnimation(fig2, upd, frames=len(y), interval=120, blit=True)
    try:
        ani.save(DOCS / "demo.gif", writer="pillow", fps=8)
    except Exception as e:
        print("gif save failed:", e)
    plt.close(fig2)
    print("wrote equity.png + demo.gif from", len(y), "points")


if __name__ == "__main__":
    main()
