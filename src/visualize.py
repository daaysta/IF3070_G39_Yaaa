import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from state import get_dim


def _draw_deck(ax, state, title):
    ship = state.ship
    cmap = plt.get_cmap("tab20")
    ax.set_xlim(0, ship.w)
    ax.set_ylim(ship.l, 0)
    ax.set_aspect("equal")
    ax.set_xticks(range(ship.w + 1))
    ax.set_yticks(range(0, ship.l + 1, 2))
    ax.grid(True, color="#cccccc", linewidth=0.5)
    ax.set_axisbelow(True)
    for i, vid in enumerate(state.inside_ids()):
        x, y, orient = state.placements[vid]
        dx, dy = get_dim(state.vehicles[vid], orient)
        ax.add_patch(Rectangle((x, y), dx, dy, facecolor=cmap(i % 20),
                               edgecolor="black", linewidth=1))
        ax.text(x + dx / 2, y + dy / 2, vid, ha="center", va="center", fontsize=7)
    outside = state.outside_ids()
    ax.set_title(f"{title}\nvalue={state.value()}  berat={state.total_weight}/"
                 f"{ship.max_capacity}  di luar={len(outside)}", fontsize=9)


def save_states_png(result, path):
    fig, axes = plt.subplots(1, 2, figsize=(10, 9))
    _draw_deck(axes[0], result.initial_state, "State awal")
    _draw_deck(axes[1], result.final_state, "State akhir")
    fig.suptitle(f"{result.name}  |  iterasi={result.iterations}  |  "
                 f"durasi={result.duration:.2f}s")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_history_png(result, path):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(len(result.history)), result.history, color="#1f77b4",
            label="maksimum")
    avg = result.extras.get("avg_history")
    if avg:
        ax.plot(range(len(avg)), avg, color="#ff7f0e", label="rata-rata populasi")
    if avg:
        ax.legend()
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Objective (total ShippingFee)")
    ax.set_title(f"{result.name}: nilai objective terhadap iterasi")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_all(result, base_path):
    save_states_png(result, f"{base_path}_states.png")
    save_history_png(result, f"{base_path}_history.png")