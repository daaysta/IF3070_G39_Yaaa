import argparse
import csv
import importlib
import json
import os
import random

from models import Vehicle, Ship
from state import State
from hill_climbing import hill_climbing_sideways
from result import SearchResult

try:
    import visualize
except ImportError:
    visualize = None

N_RUNS = 3
HC_MAX_SIDEWAYS = 100
GA_CONTROL_POP = 30
GA_ITER_VARIATIONS = (50, 100, 200)
GA_CONTROL_ITER = 100
GA_POP_VARIATIONS = (10, 30, 50)


def make_instance(seed=42, n=30, ship=None):
    rng = random.Random(seed)
    ship = ship or Ship(w=8, l=12, max_capacity=100)
    vehicles = [
        Vehicle(f"V{i + 1}", w=rng.randint(1, 3), l=rng.randint(2, 4),
                fee=rng.randint(10, 100), weight=rng.randint(2, 10),
                eta=rng.randint(1, 10))
        for i in range(n)
    ]
    return vehicles, ship


def load_instance(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [Vehicle(**v) for v in data["vehicles"]], Ship(**data["ship"])


def _load(module, attr):
    try:
        return getattr(importlib.import_module(module), attr)
    except (ImportError, AttributeError):
        return None


def _save(result, path, run_id, label):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    d = result.to_dict()
    d["run_id"], d["label"] = run_id, label
    d["final_state_text"] = result.final_state.render_text()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    if visualize is not None:
        visualize.save_all(result, visualize.plot_base(path))
    return {
        "label": label, "algorithm": result.name, "run": run_id,
        "params": json.dumps(result.params),
        "initial_value": d["initial_value"], "final_value": d["final_value"],
        "iterations": result.iterations,
        "duration_sec": round(result.duration, 4),
        "valid": d["final_state"]["valid"],
        "file": os.path.relpath(path, os.path.dirname(os.path.dirname(path))).replace("\\", "/"),
    }


def _initial(vehicles, ship, seed):
    return State.random_state(vehicles, ship, random.Random(seed))


def run_hc(vehicles, ship, out, seed):
    rows = []
    for r in range(1, N_RUNS + 1):
        s = seed + r
        res = hill_climbing_sideways(_initial(vehicles, ship, s),
                                     max_sideways=HC_MAX_SIDEWAYS,
                                     rng=random.Random(s))
        rows.append(_save(res, f"{out}/hc/run{r}.json", r, "hc_sideways"))
        print(f"[HC] run {r}: value={res.final_value} iter={res.iterations} "
              f"stop={res.extras['stop_reason']} t={res.duration:.2f}s")
    return rows


def run_sa(vehicles, ship, out, seed):
    sa = _load("simulated_annealing", "simulated_annealing")
    if sa is None:
        print("[SA] dilewati: simulated_annealing.simulated_annealing belum ada")
        return []
    rows = []
    for r in range(1, N_RUNS + 1):
        s = seed + r
        res = sa(_initial(vehicles, ship, s), rng=random.Random(s))
        rows.append(_save(res, f"{out}/sa/run{r}.json", r, "sa"))
        print(f"[SA] run {r}: value={res.final_value} iter={res.iterations} t={res.duration:.2f}s")
    return rows


def _ga_runner():
    fn = _load("ga", "genetic_algorithm")
    if fn is None:
        return None

    def run(vehicles, ship, population_size, generations, seed):
        d = fn(vehicles, ship, jumlah_populasi=population_size,
               iterasi=generations, seed=seed)
        return SearchResult(
            name="ga",
            params={"population_size": population_size,
                    "generations": generations},
            initial_state=d["state_awal"],
            final_state=d["state_akhir"],
            history=d["riwayat_max"],
            iterations=d["iterasi"],
            duration=d["durasi"],
            extras={"avg_history": d["riwayat_rata"],
                    "population_size": d["jumlah_populasi"]},
        )

    return run


def run_ga(vehicles, ship, out, seed):
    ga = _ga_runner()
    if ga is None:
        print("[GA] dilewati: ga.genetic_algorithm belum ada")
        return []
    configs = [("ga_iter", GA_CONTROL_POP, g) for g in GA_ITER_VARIATIONS]
    configs += [("ga_pop", p, GA_CONTROL_ITER) for p in GA_POP_VARIATIONS]
    rows = []
    for group, pop, gens in configs:
        for r in range(1, N_RUNS + 1):
            s = seed + r
            res = ga(vehicles, ship, population_size=pop, generations=gens, seed=s)
            label = f"{group}_pop{pop}_gen{gens}"
            rows.append(_save(res, f"{out}/ga/{label}_run{r}.json", r, label))
            print(f"[GA] {label} run {r}: value={res.final_value} t={res.duration:.2f}s")
    return rows


def write_summary(rows, out):
    if not rows:
        return
    with open(f"{out}/summary.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    with open(f"{out}/summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--out", default=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "output")))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-vehicles", type=int, default=30)
    ap.add_argument("--only", default="hc,sa,ga")
    a = ap.parse_args()

    vehicles, ship = (load_instance(a.input) if a.input
                      else make_instance(a.seed, a.n_vehicles))
    os.makedirs(a.out, exist_ok=True)
    inst = {"ship": vars(ship), "vehicles": [vars(v) for v in vehicles]}
    with open(f"{a.out}/instance.json", "w", encoding="utf-8") as f:
        json.dump(inst, f, indent=2)

    if visualize is None:
        print("matplotlib belum terpasang, PNG dilewati (py -m pip install matplotlib)")

    want = set(a.only.split(","))
    rows = []
    if "hc" in want:
        rows += run_hc(vehicles, ship, a.out, a.seed)
    if "sa" in want:
        rows += run_sa(vehicles, ship, a.out, a.seed)
    if "ga" in want:
        rows += run_ga(vehicles, ship, a.out, a.seed)
    write_summary(rows, a.out)
    print(f"selesai, hasil di {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()