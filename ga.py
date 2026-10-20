"""
ga.py - Genetic Algorithm (bagian A).

Mengacu pada slide "Beyond Classical Search" (Genetic Algorithm, slide 42-49):
  individu = State | fitness = State.value() (total ShippingFee)
  seleksi roulette wheel -> crossover satu titik potong -> mutasi peluang kecil.
Tambahan (heuristik, jelaskan di laporan):
  - repair setelah crossover lewat state_resolution agar anak selalu valid,
  - elitism (individu terbaik disalin langsung ke generasi berikutnya).
    Set elitism=0 untuk mengikuti pseudocode slide secara murni.
"""
import time

from state import State, state_resolution


def select_parent(population, fitness, rng):
    """Roulette wheel: peluang terpilih sebanding dengan fitness.
    Ditambah epsilon kecil agar tetap jalan kalau semua fitness = 0."""
    weights = [f + 1e-9 for f in fitness]
    return rng.choices(population, weights=weights, k=1)[0]


def crossover(p1, p2, rng):
    """Satu titik potong pada daftar kendaraan: gen (placement) sebelum titik
    potong dari p1, sisanya dari p2. Hasil bisa bentrok, jadi diperbaiki
    (kendaraan yang bentrok dikeluarkan dari kapal) oleh state_resolution.
    Gen p1 diproses lebih dulu sehingga menang jika terjadi konflik."""
    ids = list(p1.vehicles)
    cut = rng.randint(1, len(ids) - 1) if len(ids) > 1 else 0
    desired = {vid: (p1 if i < cut else p2).placements[vid] for i, vid in enumerate(ids)}
    return state_resolution(p1.vehicles, p1.ship, desired, order=ids)


def genetic_algorithm(vehicles, ship, population_size, iterations, rng,
                      mutation_rate=0.2, elitism=1):
    """Jalankan GA. `iterations` = jumlah generasi.

    Return dict (format sama dengan algoritma lain):
      initial        : individu terbaik pada populasi awal
      final          : individu terbaik pada populasi akhir
      history        : nilai maksimum populasi per generasi (indeks 0 = populasi awal)
      avg_history    : nilai rata-rata populasi per generasi
      duration       : detik
      iterations, population_size
      candidate_peak : nilai maksimum populasi pada generasi terakhir
    """
    start = time.perf_counter()

    population = [State.random_state(vehicles, ship, rng) for _ in range(population_size)]
    fitness = [s.value() for s in population]

    best_i = max(range(population_size), key=lambda i: fitness[i])
    initial = population[best_i]

    candidate_peak = max(fitness)                 # nilai maksimum populasi
    history = [candidate_peak]
    avg_history = [sum(fitness) / population_size]

    for _ in range(iterations):
        # Elitism: salin langsung individu terbaik (State tidak diubah in-place,
        # jadi aman dibagi tanpa copy).
        ranked = sorted(range(population_size), key=lambda i: fitness[i], reverse=True)
        new_population = [population[i] for i in ranked[:elitism]]

        while len(new_population) < population_size:
            x = select_parent(population, fitness, rng)
            y = select_parent(population, fitness, rng)
            child = crossover(x, y, rng)
            if rng.random() < mutation_rate:
                mutated = child.random_neighbor(rng)
                if mutated is not None:
                    child = mutated
            new_population.append(child)

        population = new_population
        fitness = [s.value() for s in population]
        candidate_peak = max(fitness)
        history.append(candidate_peak)
        avg_history.append(sum(fitness) / population_size)

    best_i = max(range(population_size), key=lambda i: fitness[i])
    return {
        "initial": initial,
        "final": population[best_i],
        "history": history,
        "avg_history": avg_history,
        "duration": time.perf_counter() - start,
        "iterations": iterations,
        "population_size": population_size,
        "candidate_peak": candidate_peak,
    }
