import csv
import json
import os
import random
import statistics

import matplotlib
matplotlib.use("Agg")          
import matplotlib.pyplot as plt

from models import Vehicle, Ship
from ga import genetic_algorithm

# Pengaturan percobaan 
JUMLAH_RUN = 3

KONTROL_POPULASI = 50                 # percobaan 1: populasi dikunci
VARIASI_ITERASI = [50, 100, 200]      # percobaan 1: iterasi divariasikan

KONTROL_ITERASI = 100                 # percobaan 2: iterasi dikunci
VARIASI_POPULASI = [20, 50, 100]      # percobaan 2: populasi divariasikan

WARNA_MAKS = "#1d4e89"                # garis nilai maksimum
WARNA_RATA = "#e07a1f"                # garis rata-rata

BASE = os.path.dirname(os.path.abspath(__file__))
FOLDER_OUTPUT = os.path.join(BASE, "..", "output")
FOLDER_PLOT = os.path.join(FOLDER_OUTPUT, "plots")


def buat_kasus_uji(seed=0, n=40):
    rng = random.Random(seed)
    ship = Ship(w=10, l=20, max_capacity=100)
    vehicles = [
        Vehicle(f"V{i}", w=rng.randint(1, 3), l=rng.randint(2, 4),
                fee=rng.randint(10, 90), weight=rng.randint(2, 9))
        for i in range(n)
    ]
    return vehicles, ship


def simpan_plot(hasil, nama_file, judul):
    plt.figure(figsize=(7, 4))
    plt.plot(hasil["riwayat_max"], color=WARNA_MAKS, label="Maksimum populasi")
    plt.plot(hasil["riwayat_rata"], color=WARNA_RATA, label="Rata-rata populasi")
    plt.xlabel("Iterasi (generasi)")
    plt.ylabel("Nilai objective (total ShippingFee)")
    plt.title(judul)
    plt.legend()
    plt.tight_layout()
    plt.savefig(nama_file, dpi=120)
    plt.close()


def jalankan_satu(percobaan, populasi, iterasi, run_ke, seed, vehicles, ship):
    hasil = genetic_algorithm(vehicles, ship, populasi, iterasi, seed=seed)

    nama_plot = f"{percobaan}_pop{populasi}_iter{iterasi}_run{run_ke}.png"
    judul = f"populasi={populasi}, iterasi={iterasi}, run {run_ke}"
    simpan_plot(hasil, os.path.join(FOLDER_PLOT, nama_plot), judul)

    return {
        "percobaan": percobaan,
        "populasi": populasi,
        "iterasi": iterasi,
        "run": run_ke,
        "seed": seed,
        "nilai_awal": hasil["state_awal"].value(),
        "nilai_akhir": hasil["nilai_akhir"],
        "durasi_detik": round(hasil["durasi"], 3),
        "riwayat_max": hasil["riwayat_max"],
        "riwayat_rata": hasil["riwayat_rata"],
        "state_awal": hasil["state_awal"].to_dict(),
        "state_akhir": hasil["state_akhir"].to_dict(),
        "geladak_awal": hasil["state_awal"].render_text(),
        "geladak_akhir": hasil["state_akhir"].render_text(),
        "plot": nama_plot,
    }


def main():
    os.makedirs(FOLDER_PLOT, exist_ok=True)

    vehicles, ship = buat_kasus_uji(seed=0, n=40)
    print("total fee semua kendaraan:", sum(v.fee for v in vehicles))

    konfigurasi = []
    for iterasi in VARIASI_ITERASI:
        konfigurasi.append(("iterasi_divariasikan", KONTROL_POPULASI, iterasi))
    for populasi in VARIASI_POPULASI:
        konfigurasi.append(("populasi_divariasikan", populasi, KONTROL_ITERASI))

    semua = []
    seed = 100
    for percobaan, populasi, iterasi in konfigurasi:
        for run_ke in range(1, JUMLAH_RUN + 1):
            seed += 1
            data = jalankan_satu(percobaan, populasi, iterasi, run_ke, seed, vehicles, ship)
            semua.append(data)
            print(f"{percobaan:22s} pop={populasi:3d} iter={iterasi:3d} run={run_ke} "
                  f"awal={data['nilai_awal']:5d} akhir={data['nilai_akhir']:5d} "
                  f"durasi={data['durasi_detik']}s")

    # Simpan semua hasil lengkap (JSON)
    with open(os.path.join(FOLDER_OUTPUT, "ga_results.json"), "w", encoding="utf-8") as f:
        json.dump(semua, f, indent=2)

    # Simpan ringkasan (CSV)
    kolom = ["percobaan", "populasi", "iterasi", "run", "seed",
             "nilai_awal", "nilai_akhir", "durasi_detik"]
    with open(os.path.join(FOLDER_OUTPUT, "ga_summary.csv"), "w", newline="", encoding="utf-8") as f:
        tulis = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        tulis.writeheader()
        tulis.writerows(semua)

    # Ringkasan per konfigurasi di layar
    print("\nRingkasan per konfigurasi (3 run):")
    print(f"{'percobaan':22s} {'pop':>4s} {'iter':>5s} {'rata2':>8s} {'min':>6s} {'maks':>6s} {'durasi':>8s}")
    for percobaan, populasi, iterasi in konfigurasi:
        grup = [d for d in semua
                if (d["percobaan"], d["populasi"], d["iterasi"]) == (percobaan, populasi, iterasi)]
        nilai = [d["nilai_akhir"] for d in grup]
        durasi = statistics.mean(d["durasi_detik"] for d in grup)
        print(f"{percobaan:22s} {populasi:4d} {iterasi:5d} {statistics.mean(nilai):8.1f} "
              f"{min(nilai):6d} {max(nilai):6d} {durasi:7.2f}s")


if __name__ == "__main__":
    main()