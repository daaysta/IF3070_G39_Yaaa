import random
import time

from state import State


def pilih_parent(populasi, rng, k=3):
    # tournament: ambil k acak, yang value-nya paling besar menang
    calon = rng.sample(populasi, min(k, len(populasi)))
    return max(calon, key=lambda s: s.value())


def crossover(a, b, rng):
    # one-point: sebagian kendaraan ikut parent a, sisanya parent b
    ids = list(a.vehicles)
    if len(ids) < 2:
        return a
    titik = rng.randint(1, len(ids) - 1)
    plan = {}
    for i, vid in enumerate(ids):
        induk = a if i < titik else b
        plan[vid] = induk.placements[vid]

    urutan = ids[:]
    rng.shuffle(urutan)
    return State.from_plan(a.vehicles, a.ship, plan, order=urutan)


def mutasi(s, rng):
    baru = s.random_neighbor(rng)
    return baru if baru else s


def genetic_algorithm(vehicles, ship, jumlah_populasi, iterasi,
                      mutation_rate=0.3, elite=2, seed=None):
    mulai = time.time()
    rng = random.Random(seed)

    populasi = [State.random_state(vehicles, ship, rng)
                for _ in range(jumlah_populasi)]
    state_awal = max(populasi, key=lambda s: s.value())
    terbaik_global = state_awal

    riwayat_max = [state_awal.value()]
    riwayat_rata = [sum(s.value() for s in populasi) / len(populasi)]

    for _ in range(iterasi):
        populasi.sort(key=lambda s: s.value(), reverse=True)

        baru = populasi[:min(elite, jumlah_populasi)]

        while len(baru) < jumlah_populasi:
            a = pilih_parent(populasi, rng)
            b = pilih_parent(populasi, rng)
            anak = crossover(a, b, rng)
            if rng.random() < mutation_rate:
                anak = mutasi(anak, rng)
            baru.append(anak)

        populasi = baru

        terbaik = max(populasi, key=lambda s: s.value())
        if terbaik.value() > terbaik_global.value():
            terbaik_global = terbaik

        riwayat_max.append(terbaik.value())
        riwayat_rata.append(sum(s.value() for s in populasi) / len(populasi))

    return {
        "state_awal": state_awal,
        "state_akhir": terbaik_global,
        "nilai_akhir": terbaik_global.value(),
        "riwayat_max": riwayat_max,
        "riwayat_rata": riwayat_rata,
        "jumlah_populasi": jumlah_populasi,
        "iterasi": iterasi,
        "durasi": time.time() - mulai,
    }