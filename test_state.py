"""
Tes bagian A. Jalankan dari folder src:   python test_state.py
(juga kompatibel dengan pytest)
"""
import random

from models import Vehicle, Ship
from state import State, state_resolution, HORIZONTAL, VERTICAL
from ga import genetic_algorithm, crossover
from data import sample_instance


def small_world():
    ship = Ship(w=6, l=8, max_capacity=20)
    vehicles = {
        "A": Vehicle("A", w=2, l=3, fee=30, weight=5),
        "B": Vehicle("B", w=2, l=2, fee=20, weight=4),
        "C": Vehicle("C", w=3, l=1, fee=10, weight=3),
        "D": Vehicle("D", w=1, l=1, fee=5, weight=30),   # berat melebihi kapasitas sendirian
    }
    return vehicles, ship


def test_footprint_orientasi():
    vehicles, ship = small_world()
    s = State(vehicles, ship)
    v = s.footprint("A", 1, 1, VERTICAL)      # 2 kolom x 3 baris
    assert len(v) == 6 and (2, 3) in v and (3, 3) not in v
    h = s.footprint("A", 1, 1, HORIZONTAL)    # 3 kolom x 2 baris
    assert len(h) == 6 and (3, 2) in h and (2, 3) not in h


def test_is_valid_kasus():
    vehicles, ship = small_world()
    assert State(vehicles, ship).is_valid()                                   # kosong valid
    assert State(vehicles, ship, {"A": (0, 0, VERTICAL)}).is_valid()
    assert not State(vehicles, ship, {"A": (5, 0, VERTICAL)}).is_valid()      # keluar kolom
    assert not State(vehicles, ship, {"A": (0, 6, VERTICAL)}).is_valid()      # keluar baris
    assert not State(vehicles, ship, {"A": (-1, 0, VERTICAL)}).is_valid()     # koordinat negatif
    assert not State(vehicles, ship, {"A": (0, 0, VERTICAL),
                                      "B": (1, 1, VERTICAL)}).is_valid()      # overlap
    assert State(vehicles, ship, {"A": (0, 0, VERTICAL),
                                  "B": (2, 0, VERTICAL)}).is_valid()          # bersebelahan
    assert not State(vehicles, ship, {"D": (0, 0, VERTICAL)}).is_valid()      # kapasitas


def test_value_dan_cache():
    vehicles, ship = small_world()
    s = State(vehicles, ship, {"A": (0, 0, VERTICAL), "B": (2, 0, VERTICAL)})
    assert s.value() == 50
    assert s.total_weight == 9


def test_can_place_mengabaikan_diri_sendiri():
    vehicles, ship = small_world()
    s = State(vehicles, ship, {"A": (0, 0, VERTICAL)})
    assert s.can_place("A", 0, 0, HORIZONTAL)          # diputar di tempat, boleh
    assert not s.can_place("B", 1, 1, VERTICAL)        # nabrak A
    assert s.can_place("B", 2, 0, VERTICAL)
    assert not s.can_place("D", 4, 4, VERTICAL)        # kelebihan berat


def test_swap_dengan_kendaraan_di_luar():
    vehicles, ship = small_world()
    s = State(vehicles, ship, {"A": (0, 0, VERTICAL)})
    new = s._swapped("A", "B")                         # B (luar) masuk ke posisi A, A keluar
    assert new is not None and new.is_valid()
    assert new.placements["A"] is None and new.placements["B"] == (0, 0, VERTICAL)
    assert s.placements["A"] == (0, 0, VERTICAL)       # state lama tidak berubah
    assert s._swapped("B", "C") is None                # keduanya di luar


def test_state_resolution_membuang_yang_bentrok():
    vehicles, ship = small_world()
    desired = {"A": (0, 0, VERTICAL), "B": (1, 1, VERTICAL), "C": (3, 0, HORIZONTAL), "D": None}
    s = state_resolution(vehicles, ship, desired, order=["A", "B", "C", "D"])
    assert s.is_valid()
    assert s.placements["B"] is None                   # bentrok dengan A
    assert s.placements["A"] is not None


def check_consistent(s):
    """Cache harus sama dengan hitung ulang dari nol."""
    assert s.is_valid()
    assert s.total_fee == sum(s.vehicles[v].fee for v in s.inside_ids())
    assert s.total_weight == sum(s.vehicles[v].weight for v in s.inside_ids())
    cells = sum(len(s.footprint(v, *s.placements[v])) for v in s.inside_ids())
    assert cells == sum(c is not None for row in s.grid for c in row)


def test_random_state_dan_neighbor_selalu_valid():
    vehicles, ship = sample_instance(seed=1, n=30)
    for seed in range(20):
        rng = random.Random(seed)
        s = State.random_state(vehicles, ship, rng)
        check_consistent(s)
        for _ in range(100):
            n = s.random_neighbor(rng)
            if n is not None:
                check_consistent(n)
                assert n.placements != s.placements    # benar-benar berbeda
                s = n


def test_all_neighbors_valid_dan_berbeda():
    vehicles, ship = sample_instance(seed=2, n=15)
    rng = random.Random(0)
    s = State.random_state(vehicles, ship, rng)
    count = 0
    for n in s.all_neighbors():
        check_consistent(n)
        assert n.placements != s.placements
        count += 1
    assert count > 0


def test_crossover_dan_ga():
    vehicles, ship = sample_instance(seed=3, n=25)
    rng = random.Random(0)
    p1 = State.random_state(vehicles, ship, rng)
    p2 = State.random_state(vehicles, ship, rng)
    for _ in range(50):
        check_consistent(crossover(p1, p2, rng))
    r = genetic_algorithm(vehicles, ship, population_size=20, iterations=30, rng=random.Random(1))
    check_consistent(r["final"])
    assert len(r["history"]) == 31 and len(r["avg_history"]) == 31
    assert r["history"] == sorted(r["history"])        # elitism: maksimum tidak turun
    assert r["final"].value() == r["candidate_peak"] >= r["initial"].value()


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("OK  ", t.__name__)
    print(f"\nSemua {len(tests)} tes lulus.")
