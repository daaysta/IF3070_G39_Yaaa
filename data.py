"""
data.py - Pembuat data contoh untuk uji coba.
Spesifikasi tidak menentukan format input, jadi B/C bebas menggantinya
(misal baca dari JSON). Seed yang sama menghasilkan data yang sama.
"""
import random

from models import Vehicle, Ship


def random_vehicles(n, rng, max_dim=4):
    """n kendaraan acak: ukuran 1..max_dim, fee 10..100, berat 1..10, eta 1..10."""
    return [
        Vehicle(
            id=f"V{i + 1}",
            w=rng.randint(1, max_dim),
            l=rng.randint(1, max_dim),
            fee=rng.randint(10, 100),
            weight=rng.randint(1, 10),
            eta=rng.randint(1, 10),
        )
        for i in range(n)
    ]


def default_ship():
    """Contoh dari spesifikasi: geladak 10 x 20, kapasitas 500."""
    return Ship(w=10, l=20, max_capacity=500)


def sample_instance(seed=0, n=40):
    rng = random.Random(seed)
    return random_vehicles(n, rng), default_ship()
