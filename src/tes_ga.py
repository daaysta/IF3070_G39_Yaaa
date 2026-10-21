import random
from models import Vehicle, Ship
from ga import genetic_algorithm

# geladak kecil + kapasitas ketat, kendaraan dibuat acak 
ship = Ship(w=8, l=10, max_capacity=40)
rng = random.Random(7)
vehicles = [
    Vehicle(f"V{i}", w=rng.randint(1, 3), l=rng.randint(2, 4),
            fee=rng.randint(10, 90), weight=rng.randint(2, 9))
    for i in range(15)
]
print("total fee semua kendaraan:", sum(v.fee for v in vehicles))

hasil = genetic_algorithm(vehicles, ship, jumlah_populasi=30, iterasi=100, seed=1)

print(hasil["state_awal"].render_text())
print()
print(hasil["state_akhir"].render_text())
print("valid:", hasil["state_akhir"].is_valid())
print("nilai awal:", hasil["riwayat_max"][0], "-> nilai akhir:", hasil["nilai_akhir"])
print("durasi:", round(hasil["durasi"], 3), "detik")