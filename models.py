"""
models.py - Data murni (tidak punya logika pencarian).

Satuan mengikuti spesifikasi Tubes 1 IF3070:
  - w, l       : satuan grid
  - fee        : juta rupiah
  - weight     : unit
  - eta        : sisa hari (belum dipakai di objective function wajib)
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Vehicle:
    id: str
    w: int          # width  (satuan grid)
    l: int          # length (satuan grid)
    fee: int        # ShippingFee
    weight: int
    eta: int = 0


@dataclass(frozen=True)
class Ship:
    w: int              # lebar geladak (jumlah kolom)
    l: int              # panjang geladak (jumlah baris)
    max_capacity: int   # kapasitas berat maksimum
