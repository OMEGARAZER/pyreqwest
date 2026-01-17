import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from tests.bench.latency import FULL_CONSUME_SIZE_LIMIT
from tests.bench.utils import StatsCollection, fmt_size, is_sync


def create_plot(collection: StatsCollection, comparison_lib: str) -> None:
    body_sizes = sorted({stat.body_size for stat in collection.stats if stat.lib == comparison_lib})
    concurrency_levels = sorted({stat.concurrency for stat in collection.stats if stat.lib == comparison_lib})
    self_lib = "pyreqwest_sync" if is_sync(comparison_lib) else "pyreqwest"

    fig, axes = plt.subplots(nrows=len(body_sizes), ncols=len(concurrency_levels), figsize=(18, 16))
    fig.suptitle(f"pyreqwest vs {comparison_lib}", fontsize=16, y=0.98)
    legend_colors = {"pyreqwest (st)": "lightblue", "pyreqwest (mt)": "lightblue", comparison_lib: "lightcoral"}

    for i, body_size in enumerate(body_sizes):
        ymax = 0.0

        for j, concurrency in enumerate(concurrency_levels):
            ax: Axes = axes[i][j]

            pyreqwest_st_stats = collection.find(f"{self_lib}_st", body_size, concurrency)
            pyreqwest_mt_stats = collection.find(f"{self_lib}_mt", body_size, concurrency)
            comparison_stats = collection.find(comparison_lib, body_size, concurrency)
            pyreqwest_mean = min(pyreqwest_st_stats.mean, pyreqwest_mt_stats.mean)

            stats = [pyreqwest_st_stats.timings, pyreqwest_mt_stats.timings, comparison_stats.timings]
            means = [pyreqwest_st_stats.mean, pyreqwest_mt_stats.mean, comparison_stats.mean]
            labels = ["pyreqwest (st)", "pyreqwest (mt)", comparison_lib]

            box_plot = ax.boxplot(stats, patch_artist=True, showfliers=False, tick_labels=labels, widths=0.6)
            ymax = max(ymax, ax.get_ylim()[1])

            # Color the boxes
            for patch, color in zip(box_plot["boxes"], legend_colors.values(), strict=False):
                patch.set_facecolor(color)

            # Customize subplot
            streamed = " (streamed)" if body_size > FULL_CONSUME_SIZE_LIMIT else ""
            ax.set_title(f"{fmt_size(body_size)} {streamed} @ {concurrency} concurrent", fontweight="bold", pad=10)
            ax.set_ylabel("Response Time (ms)")
            ax.grid(True, alpha=0.3)

            speedup = comparison_stats.mean / pyreqwest_mean if pyreqwest_mean != 0 else 0
            faster_lib = "pyreqwest" if speedup > 1 else comparison_lib
            pct_diff = (speedup - 1) * 100 if speedup > 1 else (1 / speedup - 1) * 100

            # Add performance annotation
            ax.text(
                0.5,
                0.95,
                f"{faster_lib}\n{pct_diff:.1f}% faster",
                transform=ax.transAxes,
                ha="center",
                va="top",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "wheat", "alpha": 0.8},
                fontsize=9,
                fontweight="bold",
            )

            # Add mean time annotations
            for i_mean, mean in enumerate(means):
                ax.text(
                    i_mean + 1,
                    mean,
                    f"{mean:.3f}ms",
                    ha="left",
                    va="center",
                    fontsize=8,
                    color="darkred" if i_mean == len(means) - 1 else "darkblue",
                    fontweight="bold",
                )

        for j, _ in enumerate(concurrency_levels):
            axes[i][j].set_ylim(ymin=0, ymax=ymax * 1.01)  # Uniform y-axis per row

    # Add overall legend
    legends = [
        Rectangle(xy=(0, 0), width=1, height=1, label=label, facecolor=color) for label, color in legend_colors.items()
    ]
    fig.legend(handles=legends, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=2)

    plt.tight_layout()
    plt.subplots_adjust(top=0.94, bottom=0.06)  # Make room for suptitle and legend

    # Save the plot
    img_path = Path(__file__).parent / f"benchmark_{comparison_lib}.png"
    plt.savefig(str(img_path), dpi=300, bbox_inches="tight")
    print(f"Plot saved as '{img_path}'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Performance latency")
    parser.add_argument("--lib", type=str)
    args = parser.parse_args()

    create_plot(collection=StatsCollection.load(), comparison_lib=args.lib)


if __name__ == "__main__":
    main()
