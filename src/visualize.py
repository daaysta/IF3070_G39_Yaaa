import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from state import get_dim

WARNA_UTAMA = "#1d4e89"
WARNA_RATA = "#e07a1f"


def plot_objective(result, path):
    avg = result.extras.get("avg_history")
    plt.figure(figsize=(7, 4))
    plt.plot(result.history, color=WARNA_UTAMA,
             label="maksimum populasi" if avg else "nilai objective")
    if avg:
        plt.plot(avg, color=WARNA_RATA, label="rata-rata populasi")
    plt.xlabel("Iterasi")
    plt.ylabel("Nilai objective (total ShippingFee)")
    plt.title(f"{result.name} {result.params}", fontsize=9)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def gambar_state(state, path, judul):
    ship = state.ship
    fig, ax = plt.subplots(figsize=(4, 7))
    ax.set_xlim(0, ship.w)
    ax.set_ylim(ship.l, 0)          
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), ship.w, ship.l, fill=False, linewidth=2))
    warna = plt.get_cmap("tab20")
    for i, (vid, p) in enumerate(state.placements.items()):
        if p is None:
            continue
        x, y, o = p
        dx, dy = get_dim(state.vehicles[vid], o)
        ax.add_patch(Rectangle((x, y), dx, dy, facecolor=warna(i % 20),
                               edgecolor="black"))
        ax.text(x + dx / 2, y + dy / 2, vid, ha="center", va="center", fontsize=7)
    ax.set_title(f"{judul}\nvalue={state.value()}, di luar kapal: {len(state.outside_ids())}",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def save_all(result, base):
    plot_objective(result, base + "_objective.png")
    gambar_state(result.initial_state, base + "_awal.png", "State awal")
    gambar_state(result.final_state, base + "_akhir.png", "State akhir")