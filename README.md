# Tugas Besar 1 IF3070 — Dasar Inteligensi Artifisial 2026/2027

## Deskripsi Proyek

PT Owen Intim Line mengoperasikan kapal kargo pengangkut kendaraan. Pada setiap jadwal keberangkatan, perusahaan menerima daftar kendaraan dengan dimensi, berat, tarif pengiriman (*ShippingFee*), dan ETA yang berbeda. Penempatan kendaraan secara manual berpotensi menyebabkan ruang geladak kurang termanfaatkan dan keuntungan pengiriman tidak optimal.

Proyek ini bertujuan membangun **sistem pendukung keputusan** untuk menentukan kendaraan yang diangkut, posisi penempatan, serta orientasi kendaraan di geladak kapal agar total *ShippingFee* maksimum dengan tetap memenuhi seluruh batasan yang ditentukan.

Karena ruang pencarian bersifat kombinatorial, meliputi pemilihan subset kendaraan, koordinat penempatan, dan orientasi, permasalahan diselesaikan menggunakan pendekatan *local search* dan algoritma optimasi berikut:

- Hill-Climbing (termasuk varian *sideways move*)
- Simulated Annealing
- Genetic Algorithm

## Setup

Pastikan Python telah terpasang, kemudian instal seluruh dependensi dengan menjalankan perintah berikut dari root repository:

```bash
pip install -r requirements.txt
```

## Cara Menjalankan

Jalankan program dari root repository.

### Menjalankan Algoritma Tertentu

```bash
python -m src.main --instance data/instance_example.json --algo steepest
```

Parameter `--algo` mendukung pilihan berikut:

| Algoritma | Deskripsi |
|---|---|
| `steepest` | Steepest-Ascent Hill-Climbing |
| `stochastic` | Stochastic Hill-Climbing |
| `sideways` | Hill-Climbing dengan *sideways move* |
| `restart` | Random-Restart Hill-Climbing |
| `sa` | Simulated Annealing |
| `ga` | Genetic Algorithm |

### Menjalankan Semua Algoritma

```bash
python -m src.main --instance data/instance_example.json --all
```

Opsi `--all` menjalankan seluruh algoritma sekaligus, termasuk eksperimen Genetic Algorithm.

### Menampilkan Initial State

Jika opsi `--algo` dan `--all` tidak diberikan, program akan menampilkan satu *initial state* secara acak.

### Parameter Tambahan

Program menyediakan beberapa parameter konfigurasi:

| Parameter | Kegunaan |
|---|---|
| `--runs` | Menentukan jumlah pengulangan eksperimen |
| `--seed` | Mengatur *random seed* untuk eksperimen yang dapat direproduksi |
| `--out` | Menentukan direktori keluaran |
| `--max-restart` | Mengatur batas jumlah restart |
| `--initial-temp` | Mengatur temperatur awal Simulated Annealing |
| `--population-size` | Mengatur ukuran populasi Genetic Algorithm |
| `--iterations` | Mengatur jumlah iterasi algoritma |

Parameter algoritma lainnya dapat disesuaikan sesuai konfigurasi yang tersedia pada program.

## Output

Hasil setiap eksperimen disimpan dalam direktori:

```text
output/<instance>/<algoritma>/
```

Output mencakup:

- **JSON** — menyimpan hasil eksperimen.
- **Visualisasi** — satu gambar yang memuat *initial state*, *final state*, dan plot hasil eksperimen.

## Instance

Tersedia enam instance permasalahan di dalam direktori `data/`.

| No. | Nama Instance | File |
|---:|---|---|
| 1 | Example | `data/instance_example.json` |
| 2 | Multiship | `data/instance_multiship.json` |
| 3 | Small | `data/instance_small.json` |
| 4 | Tight Space | `data/instance_tight_space.json` |
| 5 | Tight Weight | `data/instance_tight_weight.json` |
| 6 | Multiship Hard | `data/instance_multiship_hard.json` |

## Anggota Kelompok dan Kontribusi

| Nama | NIM | Kontribusi |
|---|---|---|
| Dastya | 11523033 | Genetic Algorithm, validasi constraint, implementasi tiga jenis move, initial state, dan kelas `State` |
| Stella Cometta Febriana | 1822435 | Implementasi Simulated Annealing, penyusunan laporan deskripsi persoalan, pembahasan implementasi (Bagian 2.1), penyusunan plot, dan visualisasi geladak |
| Nathan Pasha Athalla | 1824053 | analisis  Hill-Climbing  |

## Tujuan Proyek

Proyek ini mengevaluasi penerapan algoritma pencarian dan optimasi dalam menyelesaikan masalah penempatan kendaraan pada geladak kapal dengan mempertimbangkan batasan penempatan dan memaksimalkan total *ShippingFee*.

Perbandingan algoritma dilakukan melalui hasil eksperimen pada berbagai instance untuk mengamati kualitas solusi dan perilaku pencarian masing-masing algoritma.
