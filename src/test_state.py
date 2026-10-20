import random
from models import Vehicle, Ship
from state import State

ship = Ship(w=10, l=20, max_capacity=500)
vehicles = [
    Vehicle("A", w=2, l=3, fee=30, weight=4),
    Vehicle("B", w=2, l=3, fee=50, weight=4),
    Vehicle("C", w=1, l=2, fee=10, weight=2),
]


# 1. rencana valid: semua harus masuk
plan = {"A": (0, 0, "H"), "B": (0, 5, "H"), "C": (5, 0, "V")}
s = State.from_plan(vehicles, ship, plan)
assert s.is_valid()
assert s.value() == 90
assert s.outside_ids() == []


# 2. rencana bentrok: B menimpa A, jadi B harus tersingkir
plan = {"A": (0, 0, "H"), "B": (1, 0, "H")}
s = State.from_plan(vehicles, ship, plan)
assert s.is_valid()
assert "A" in s.inside_ids()
assert "B" in s.outside_ids()
assert s.value() == 30


# 3. keluar batas: C horizontal di x=9 butuh kolom 9 dan 10 (geladak cuma sampai 9)
plan = {"C": (9, 0, "H")}
s = State.from_plan(vehicles, ship, plan)
assert s.is_valid()
assert "C" in s.outside_ids()
assert s.value() == 0


# 4. kelebihan berat: kapasitas 5, A (4) masuk, C (2) tidak muat
kecil = Ship(w=10, l=20, max_capacity=5)
plan = {"A": (0, 0, "H"), "C": (5, 0, "V")}
s = State.from_plan(vehicles, kecil, plan)
assert s.is_valid()
assert "A" in s.inside_ids()
assert "C" in s.outside_ids()
assert s.total_weight <= 5

# 5. random_state dan rantai neighbor harus selalu valid
for seed in range(200):
    rng = random.Random(seed)
    s = State.random_state(vehicles, ship, rng)
    assert s.is_valid(), f"random_state tidak valid, seed={seed}"
    for _ in range(30):
        n = s.random_neighbor(rng)
        if n is None:
            break
        assert n.is_valid(), f"neighbor tidak valid, seed={seed}"
        s = n


# 6. cache harus sama dengan hitungan dari nol
rebuilt = State(vehicles, ship, )

# 7. all_neighbors: semuanya valid
s = State.random_state(vehicles, ship, random.Random(1))
jumlah = 0
for n in s.all_neighbors():
    assert n.is_valid()
    jumlah += 1
print("jumlah neighbor:", jumlah)

print("semua test lolos")